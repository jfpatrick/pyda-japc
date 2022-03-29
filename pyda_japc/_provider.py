import functools
import typing
import jpype as jp
import concurrent.futures
import pyda.providers
import pyda.data
# TODO: Using private interface, because pyda for
#  now does not offer complete public API
import pyda.providers._core

from . import _transformations
from . import _jpype_tools


if typing.TYPE_CHECKING:
    from pyda.data import PropertyAccessQuery
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

    # TODO: SET is not yet available in PyDA
    # def set(self, device_name, property_name, value, selector):
    #     # Note that device_name may contain a protocol and service.
    #     cern = _jpype_tools.cern_pkg()
    #     mpv = _transformations.DataTypeValue_to_MapParameterValue(value)  # TODO: This should become AnyData_to_MapParameterValue
    #     factory = param_factory()
    #     param = factory.newParameter(f'{device_name}/{property_name}')
    #     selector_j = cern.japc.core.factory.SelectorFactory.newSelector(selector)
    #     param.setValue(selector_j, mpv)


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
            # FIXME: This is really backwards, but what's the best practice to set __cause__?
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
