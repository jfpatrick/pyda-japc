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
    assert isinstance(response, pyda.data.PropertyAccessResponse)
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
    assert isinstance(response, pyda.data.PropertyAccessResponse)
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
                assert isinstance(response, pyda.data.PropertyAccessResponse)
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
                assert isinstance(response, pyda.data.PropertyAccessResponse)
                assert isinstance(response.exception, pyda.data.PropertyAccessError)
                assert str(response.exception) == "Test error"
                assert isinstance(response.exception.__cause__, cern.japc.core.ParameterException)
                assert response.exception.__cause__.getMessage() == "Test error"
                break


# TODO: For the future, when SET is implemented
# @pytest.mark.parametrize("selector", ["", "TEST.USER.ALL"])
# def test_set(japc_mock, selector):
#     dev = "MockedDevice"
#     prop = "MockedProperty"
#     param = japc_mock.mockParameter(f"{dev}/{prop}")
#     org = jpype.JPackage("org")
#     input_val = model.AnyData.create()
#     input_val["field1"] = "one"
#     input_val["field2"] = "two"
#     expected_mpv = japc_mock.mpv(["field1", "field2"], ["one", "two"])
#     expected_sel = japc_mock.sel(selector)
#     api.set(dev, prop, input_val, selector)
#     org.mockito.Mockito.verify(param).setValue(expected_sel, expected_mpv)
#
# 
# @pytest.mark.parametrize("selector", ["", "TEST.USER.ALL"])
# def test_set_invalid(japc_mock, selector, cern):
#     dev = "MockedDevice"
#     prop = "MockedProperty"
#     param = japc_mock.mockParameter(f"{dev}/{prop}")
#     org = jpype.JPackage("org")
#     org.mockito.Mockito.doThrow(japc_mock.pe("Test error")) \
#         .when(param) \
#         .setValue(cern.japc.ext.mockito.JapcMatchers.anySelector(),
#                   cern.japc.ext.mockito.JapcMatchers.anyParameterValue())
#     input_val = model.AnyData.create()
#     input_val["field1"] = "one"
#     input_val["field2"] = "two"
#     with pytest.raises(cern.japc.core.ParameterException) as e:
#         api.set(dev, prop, input_val, selector)
#         assert e.getMessage() == "Test error"
