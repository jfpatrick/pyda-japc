import jpype as jp
import numpy as np
import pytest
import pyda
import pyda.data
import pyda_japc


@pytest.mark.parametrize("selector", ["", "TEST.USER.ALL"])
def test__JapcProvider__get_property__value(mock_acq_param, japc_mock, selector):
    dev = "MockedDevice"
    prop = "MockedProperty"
    mpv = japc_mock.mpv(["field1", "field2"], [123, 456])

    mock_acq_param(dev, prop, selector, mpv)
    provider = pyda_japc.JapcProvider()
    client = pyda.SimpleClient(provider=provider)
    response = client.get(device=dev, prop=prop, selector=selector)
    assert isinstance(response, pyda.data.PropertyRetrievalResponse)
    assert response.value["field1"] == 123
    assert response.value["field2"] == 456


@pytest.mark.parametrize("selector", ["", "TEST.USER.ALL"])
def test__JapcProvider__get_property__exception(mock_acq_param, selector, cern):
    dev = "MockedDevice"
    prop = "MockedProperty"
    mock_acq_param(dev, prop, selector, Exception("Test error"))

    provider = pyda_japc.JapcProvider()
    client = pyda.SimpleClient(provider=provider)
    response = client.get(device=dev, prop=prop, selector=selector)
    assert isinstance(response, pyda.data.PropertyRetrievalResponse)
    assert isinstance(response.exception, pyda.data.PropertyAccessError)
    assert str(response.exception) == "Test error"
    assert isinstance(response.exception.__cause__, cern.japc.core.ParameterException)
    assert response.exception.__cause__.getMessage() == "Test error"


@pytest.mark.parametrize("selector", ["", "TEST.USER.ALL"])
def test__JapcProvider__subscriptions__value(japc_mock, selector, supercycle_mock, mock_acq_param):
    dev = "MockedDevice"
    prop = "MockedProperty"
    mock_acq_param(dev, prop, selector, japc_mock.mpv(["field1", "field2"], [123, 456]))

    provider = pyda_japc.JapcProvider()
    client = pyda.SimpleClient(provider=provider)

    with supercycle_mock(selector):
        sub = client.subscribe(device='MockedDevice', prop='MockedProperty', selector=selector)
        sub.start()
        with sub:
            for response in sub:
                assert isinstance(response, pyda.data.PropertyRetrievalResponse)
                assert response.value["field1"] == 123
                assert response.value["field2"] == 456
                break


@pytest.mark.parametrize("selector", ["", "TEST.USER.ALL"])
def test__JapcProvider__subscriptions__exception(selector, supercycle_mock, mock_acq_param, cern):
    dev = "MockedDevice"
    prop = "MockedProperty"
    mock_acq_param(dev, prop, selector, Exception("Test error"))

    provider = pyda_japc.JapcProvider()
    client = pyda.SimpleClient(provider=provider)

    with supercycle_mock(selector):
        sub = client.subscribe(device='MockedDevice', prop='MockedProperty', selector=selector)
        sub.start()
        with sub:
            for response in sub:
                assert isinstance(response, pyda.data.PropertyRetrievalResponse)
                assert isinstance(response.exception, pyda.data.PropertyAccessError)
                assert str(response.exception) == "Test error"
                assert isinstance(response.exception.__cause__, cern.japc.core.ParameterException)
                assert response.exception.__cause__.getMessage() == "Test error"
                break


@pytest.mark.parametrize("selector", ["", "TEST.USER.ALL"])
def test__JapcProvider__set_pure_python(japc_mock, selector):
    dev = "MockedDevice"
    prop = "MockedProperty"
    param = japc_mock.mockParameter(f"{dev}/{prop}")
    org = jp.JPackage("org")
    input_val = {'field1': "one", "field2": np.int8(2), "field3": 3.14}
    expected_mpv = japc_mock.mpv(["field1", "field2", "field3"], ["one", jp.JByte(2), 3.14])
    expected_sel = japc_mock.sel(selector)

    provider = pyda_japc.JapcProvider()
    client = pyda.SimpleClient(provider=provider)

    response = client.set(device=dev, prop=prop, selector=selector, value=input_val)
    org.mockito.Mockito.verify(param).setValue(expected_sel, expected_mpv)
    assert isinstance(response, pyda.data.PropertyUpdateResponse)


@pytest.mark.parametrize("selector", ["", "TEST.USER.ALL"])
def test__JapcProvider__set(japc_mock, selector, setting_data_type_value):
    dev = "MockedDevice"
    prop = "MockedProperty"
    param = japc_mock.mockParameter(f"{dev}/{prop}")
    org = jp.JPackage("org")
    input_val = setting_data_type_value(selector)
    input_val["field1"] = "one"
    input_val["field2"] = "two"
    expected_mpv = japc_mock.mpv(["field1", "field2"], ["one", "two"])
    expected_sel = japc_mock.sel(selector)

    provider = pyda_japc.JapcProvider()
    client = pyda.SimpleClient(provider=provider)

    response = client.set(device=dev, prop=prop, selector=selector, value=input_val)
    org.mockito.Mockito.verify(param).setValue(expected_sel, expected_mpv)
    assert isinstance(response, pyda.data.PropertyUpdateResponse)
    # TODO: Current implementation does not include value. Needs discussion
    # assert response.value["field1"] == "one"
    # assert response.value["field2"] == "two"


@pytest.mark.parametrize("selector", ["", "TEST.USER.ALL"])
def test__JapcProvider__set_exception(japc_mock, selector, cern, setting_data_type_value):
    dev = "MockedDevice"
    prop = "MockedProperty"
    param = japc_mock.mockParameter(f"{dev}/{prop}")
    org = jp.JPackage("org")
    # TODO: Do a better selector matcher
    org.mockito.Mockito.doThrow(japc_mock.pe("Test error")) \
        .when(param) \
        .setValue(cern.japc.ext.mockito.JapcMatchers.anySelector(),
                  cern.japc.ext.mockito.JapcMatchers.anyParameterValue())
    input_val = setting_data_type_value(selector)
    input_val["field1"] = "one"
    input_val["field2"] = "two"

    provider = pyda_japc.JapcProvider()
    client = pyda.SimpleClient(provider=provider)

    response = client.set(device=dev, prop=prop, selector=selector, value=input_val)
    assert isinstance(response, pyda.data.PropertyUpdateResponse)
    assert isinstance(response.exception, pyda.data.PropertyAccessError)
    assert str(response.exception) == "Test error"
    assert isinstance(response.exception.__cause__, cern.japc.core.ParameterException)
    assert response.exception.__cause__.getMessage() == "Test error"
