import cmmnbuild_dep_manager
import jpype as jp
import pytest


@pytest.fixture
def jvm() -> None:
    mgr = cmmnbuild_dep_manager.Manager()
    if not mgr.is_resolved():
        mgr.resolve()
    mgr.start_jpype_jvm()


@pytest.fixture
def japc_mock(jvm):
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

    """
    mock = jp.JPackage("cern").japc.ext.mockito.JapcMock

    try:
        mock.mockAllServices()
        yield mock
    finally:
        mock.resetToDefault()
