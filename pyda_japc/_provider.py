import functools
import typing
import jpype as jp
import concurrent.futures
import pyda.providers
import pyda.data
import pyrbac
# TODO: Using private interface, because pyda for
#  now does not offer complete public API
import pyda.providers._core

from . import _transformations
from . import _jpype_tools


if typing.TYPE_CHECKING:
    from pyda.data import PropertyAccessQuery, PropertyUpdateResponse
    cern = jp.JPackage('cern')


class JapcPropertyStream(pyda.providers._core.BasePropertyStream):

    def __init__(self, query: "PropertyAccessQuery"):
        super().__init__()

        param_j = create_param(query)
        selector_j = create_selector(query)
        listener_j = create_value_listener(query, self._response_received)

        self._sh_j = param_j.createSubscription(selector_j, listener_j)
        self._sh_j.startMonitoring()

    def start(self, stream_handler):
        super().start(stream_handler)
        self._sh_j.startMonitoring()

    def stop(self, stream_handler):
        self._sh_j.stopMonitoring()
        super().stop(stream_handler)


class JapcProvider(pyda.providers.BaseProvider):

    def __init__(self, *, rbac_token: typing.Union[pyrbac.Token, bytes, None] = None):
        super().__init__()
        self.rbac_token = rbac_token

    @property
    def rbac_token(self) -> typing.Optional[pyrbac.Token]:
        token_holder = get_token_holder()
        token_j = token_holder.getRbaToken()
        if token_j is None:
            return None
        return pyrbac.Token(token_j.getEncoded())

    @rbac_token.setter
    def rbac_token(self, new_token: typing.Union[pyrbac.Token, bytes, None]):
        token_holder = get_token_holder()
        if new_token is None:
            token_holder.clear()
            return
        buffer: bytes = (new_token.get_encoded()
                         if isinstance(new_token, pyrbac.Token) else new_token)
        try:
            token_j = token_from_bytes(buffer)
        except Exception as e:  # noqa: B902
            # Can fail, e.g. with error
            # cern.rbac.common.TokenFormatException:
            # Token's signature is invalid - only tokens issued by the RBAC <RBAC_ENV> Server are accepted.
            # TODO: Should we wrap this error into a Python error? Or just let it pass through?
            return
        token_holder.setRbaToken(token_j)

    def _get_property(self, query: "PropertyAccessQuery"):
        # A non-blocking get.
        future = concurrent.futures.Future()

        param_j = create_param(query)
        selector_j = create_selector(query)
        listener_j = create_value_listener(query, future.set_result)

        param_j.getValue(selector_j, listener_j)
        return future

    def _create_property_stream(self, query: "PropertyAccessQuery"):
        return JapcPropertyStream(query)

    def _set_property(
            self,
            query: "PropertyAccessQuery",
            value: typing.Any,
    ):
        # A non-blocking set.
        future = concurrent.futures.Future()

        param_j = create_param(query)
        selector_j = create_selector(query)

        # FIXME: This listener probably has to have a different valueReceived implementation
        #  because the received object from japc is mostly dummy (it returns the same data that
        #  was set), and we need to produce a
        #  PropertyUpdateResponse (same type for exception actually)
        listener_j = create_set_value_listener(query, future.set_result)

        # TODO: This should also be able to convert a simple dictionary
        #  (or other arbitrary types in future DSF)
        mpv = _transformations.DataTypeValue_to_MapParameterValue(value)

        param_j.setValue(selector_j, mpv, listener_j)
        return future


def token_from_bytes(buffer: bytes):
    cern = _jpype_tools.cern_pkg()
    java = jp.java
    return cern.rbac.common.RbaToken.parseAndValidate(java.nio.ByteBuffer.wrap(buffer))


def get_token_holder():
    cern = _jpype_tools.cern_pkg()
    return cern.rbac.util.holder.ClientTierTokenHolder


def create_param(query: "PropertyAccessQuery"):
    cern = _jpype_tools.cern_pkg()
    factory = param_factory()
    param = factory.newParameter(f'{query.device}/{query.prop}')
    return param


def create_selector(query: "PropertyAccessQuery"):
    cern = _jpype_tools.cern_pkg()
    if not query.selector and not query.data_filters:
        return cern.japc.core.Selectors.NO_SELECTOR
    if query.data_filters:
        data_filter_j = create_data_filter(query.data_filters)
        return cern.japc.core.factory.SelectorFactory.newSelector(str(query.selector), data_filter_j)
    return cern.japc.core.factory.SelectorFactory.newSelector(str(query.selector))


def create_value_listener(query: "PropertyAccessQuery", callback: typing.Callable[["PropertyRetrievalResponse"], None]):
    cern = _jpype_tools.cern_pkg()

    def on_exception(_, __, exception_j: "cern.japc.core.ParameterException"):
        _, notification_type = _transformations.ValueHeader_to_ctx_notif_pair(exception_j.getHeader())
        try:
            # Raise a ``PropertyAccessError``, and then immediately catch it and present it to the ``PropertyUpdateResponse``.
            # TODO: Investigate if there is a better way to construct an exception with a correct
            #  ``__cause__`` without having to try & except like this.
            raise pyda.data.PropertyAccessError(exception_j.getMessage()) from exception_j
        except pyda.data.PropertyAccessError as error:
            response = pyda.data.PropertyRetrievalResponse(
                query=query,
                notification_type=notification_type,
                exception=error,
            )
            callback(response)

    def on_val_recv(_, apv_j):
        value, notification_type = _transformations.AcquiredParameterValue_to_AcquiredPropertyData_notif_pair(apv_j)
        response = pyda.data.PropertyRetrievalResponse(
            query=query,
            notification_type=notification_type,
            value=value,
        )
        callback(response)

    return jp.JProxy(
        cern.japc.core.ParameterValueListener,
        {
            'exceptionOccured': on_exception,
            'valueReceived': on_val_recv
        }
    )


# TODO: Maybe this is not needed at all (if PropertyAccessReponse can be used for SET)?
def create_set_value_listener(query: "PropertyAccessQuery", callback: typing.Callable[["PropertyUpdateResponse"], None]):
    cern = _jpype_tools.cern_pkg()

    def on_exception(_, __, exception_j: "cern.japc.core.ParameterException"):
        try:
            # Raise a ``PropertyAccessError``, and then immediately catch it and present it to the ``PropertyUpdateResponse``.
            # TODO: Investigate if there is a better way to construct an exception with a correct
            #  ``__cause__`` without having to try & except like this.
            raise pyda.data.PropertyAccessError(exception_j.getMessage()) from exception_j
        except pyda.data.PropertyAccessError as error:
            response = pyda.data.PropertyUpdateResponse(
                query=query,
                exception=error,
            )
            callback(response)

    def on_val_recv(_, apv_j):
        selector = apv_j.getHeader().getSelector().getId()
        header = pyda.data.UpdateHeader(selector)
        response = pyda.data.PropertyUpdateResponse(
            query=query,
            header=header,
        )
        callback(response)

    return jp.JProxy(
        cern.japc.core.ParameterValueListener,
        {
            'exceptionOccured': on_exception,
            'valueReceived': on_val_recv
        }
    )


def create_data_filter(py_filter: typing.Mapping[str, typing.Any]):
    cern = _jpype_tools.cern_pkg()
    res = cern.japc.core.factory.MapParameterValueFactory.newValue()
    for key, val in py_filter.items():
        # FIXME: This conversion needs to carefully
        #  convert all to Java types
        res.put(key, val)
    return res


@functools.lru_cache()
def param_factory() -> "cern.japc.core.factory.ParameterFactory":
    cern = _jpype_tools.cern_pkg()
    return cern.japc.core.factory.ParameterFactory.newInstance()
