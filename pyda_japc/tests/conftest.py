import cmmnbuild_dep_manager
import contextlib
import jpype as jp
import pytest
from pyda_japc import _jpype_tools


@pytest.fixture(scope='session')
def jvm() -> None:
    mgr = cmmnbuild_dep_manager.Manager()
    if not mgr.is_resolved():
        mgr.resolve()
    if not jp.isJVMStarted():
        mgr.start_jpype_jvm()


@pytest.fixture
def cern(jvm):
    # Convenience accessor
    return _jpype_tools.cern_pkg()


@pytest.fixture
def japc_mock(jvm, cern):
    """
    Provide a JAPC mock instance that has some interesting capabilities:

        acqVal = cern.japc.ext.mockito.JapcMock.acqVal
        mockAllServices = cern.japc.ext.mockito.JapcMock.mockAllServices
        mockParameter = cern.japc.ext.mockito.JapcMock.mockParameter
        mpv = cern.japc.ext.mockito.JapcMock.mpv
        pe = cern.japc.ext.mockito.JapcMock.pe
        resetJapcMock = cern.japc.ext.mockito.JapcMock.resetJapcMock
        resetToDefault = cern.japc.ext.mockito.JapcMock.resetToDefault
        sel = cern.japc.ext.mockito.JapcMock.sel
        whenGetValueThen = cern.japc.ext.mockito.JapcMock.whenGetValueThen
        setGlobalAnswer = cern.japc.ext.mockito.JapcMock.setGlobalAnswer
        spv = cern.japc.ext.mockito.JapcMock.spv
        verify = org.mockito.Mockito.verify
        newSuperCycle = cern.japc.ext.mockito.JapcMock.newSuperCycle

    Implementation: https://gitlab.cern.ch/acc-co/japc/japc-core/-/blob/master/japc-ext-mockito/src/java/cern/japc/ext/mockito/JapcMock.java#L61
    """
    mock = cern.japc.ext.mockito.JapcMock

    try:
        mock.mockAllServices()
        yield mock
    finally:
        mock.resetToDefault()
        mock.mockNoService()


@pytest.fixture
def supercycle_mock(japc_mock, cern):
    # Supercycle mock is needed for testing subscriptions for specific selectors

    @contextlib.contextmanager
    def _wrapper(selector: str):
        cycle_id = selector or cern.japc.core.Selectors.NO_SELECTOR.getId()
        supercycle = japc_mock.newSuperCycle(cern.japc.ext.mockito.Cycle(cycle_id, 1000))
        supercycle.start()
        try:
            yield
        finally:
            supercycle.stop()

    return _wrapper


@pytest.fixture
def mock_acq_param(japc_mock, cern):

    def wrapper(device: str, prop: str, sel: str, *values):
        param_name = f"{device}/{prop}"

        def map_value_to_acq_value_with_selector(val):
            # japc-ext-mockito lacks some convenience methods, and always produces values with empty header,
            # which contains selector "__unknown_selector__". This breaks DSF selector parsing when acquired
            # value's header is given to model's CycleBoundAcquisitionContext. Therefore, we call into JAPC
            # to produce a value with the header that contains proper selector
            factory = cern.japc.core.factory
            header = factory.ValueHeaderFactory.newAcquisitionRegularUpdateHeader(0, 0, sel)

            if isinstance(val, cern.japc.value.ParameterValue):
                apv = factory.AcquiredParameterValueFactory.newAcquiredParameterValue(
                    param_name,
                    header,
                    val,
                )
                return apv
            elif isinstance(val, Exception):
                exc = japc_mock.pe(str(val), header)
                return exc
            else:
                raise TypeError(f"Can't handle type {type(val)} of {val}")

        param = japc_mock.mockParameter(param_name)
        selector = (japc_mock.sel(sel) if sel
                    else cern.japc.ext.mockito.JapcMatchers.anySelectorMatcher())
        japc_mock.whenGetValueThen(
            param,
            selector,
            *map(map_value_to_acq_value_with_selector, values),
        )
        return param

    return wrapper
