import jpype as jp
import numpy as np
import numpy.testing
import pyds_model as model
import pyda.data
import pytest

import pyda_japc._transformations as trans


@pytest.fixture
def datatype():
    class_ = model.DeviceClass.create("test_class", "0.0.1")
    p = class_.create_acquisition_property("test_prop")
    return p.mutable_data_type


@pytest.mark.parametrize(
    ["input_type_name", "output_type_name"],
    [
        ("BOOLEAN", "BOOL"),
        ("BYTE", "INT8"),
        ("SHORT", "INT16"),
        ("INT", "INT32"),
        ("LONG", "INT64"),
        ("FLOAT", "FLOAT"),
        ("DOUBLE", "DOUBLE"),
        ("STRING", "STRING"),
    ],
)
def test_value_type_to_basic_type(cern, input_type_name, output_type_name):
    ValueType = cern.japc.value.ValueType
    input_type = getattr(ValueType, input_type_name)
    output_type = getattr(model.BasicType, output_type_name)
    assert trans.ValueType_to_BasicType(input_type) == output_type


def test_value_type_to_basic_type_missing(jvm):
    with pytest.raises(TypeError, match='Unknown type None'):
        trans.ValueType_to_BasicType(None)


def test_mapparametervalue_to_datatypevalue_multiple_values(japc_mock, cern):
    japc_value = cern.japc.value.spi.value
    mpv = japc_mock.mpv(
        ['a_byte', 'a_short'], [
            japc_value.simple.ByteValue(127),
            japc_value.simple.ShortValue(2),
        ]
    )
    result = trans.MapParameterValue_to_DataTypeValue(mpv)
    assert isinstance(result, model.DataTypeValue)
    assert sorted(result.keys()) == ['a_byte', 'a_short']
    assert result.get_type('a_byte') == model.BasicType.INT8
    assert result['a_byte'] == 127
    assert result.get_type('a_short') == model.BasicType.INT16
    assert result['a_short'] == 2


@pytest.mark.parametrize(
    ["simple_value_type", "expected_type_name", "value"],
    [
        ("BooleanValue", "BOOL", True),
        ("ByteValue", "INT8", 127),
        ("ShortValue", "INT16", 135),
        ("IntValue", "INT32", 135),
        ("LongValue", "INT64", 135),
        ("FloatValue", "FLOAT", 3.140000104904175),  # We lack precision when re-creating the Python float from float32.
        ("DoubleValue", "DOUBLE", 3.14),
        ("StringValue", "STRING", "Hello world! ✓"),
    ],
)
def test_mapparametervalue_to_datatypevalue__specific_types(japc_mock, cern, simple_value_type, expected_type_name, value):
    japc_value = cern.japc.value.spi.value
    jvalue = getattr(japc_value.simple, simple_value_type)(value)

    mpv = japc_mock.mpv(['a_name'], [jvalue])
    result = trans.MapParameterValue_to_DataTypeValue(mpv)
    assert isinstance(result, model.DataTypeValue)
    assert 'a_name' in result
    expected_type = getattr(model.BasicType, expected_type_name)
    assert result.get_type('a_name') == expected_type
    assert result['a_name'] == value


@pytest.mark.parametrize(
    ["simple_value_type", "expected_type_name", "value"],
    [
        ("BooleanArrayValue", "BOOL", np.array([True, False, True], dtype=np.bool)),
        ("ByteArrayValue", "INT8", np.array([127, 0, -3], dtype=np.int8)),
        ("ShortArrayValue", "INT16", np.array([135, 234], dtype=np.int16)),
        ("IntArrayValue", "INT32", np.array([135, 234], dtype=np.int32)),
        ("LongArrayValue", "INT64", np.array([135, 234], dtype=np.int64)),
        ("FloatArrayValue", "FLOAT", np.array([3.140000104904175, 0.5], dtype=np.float32)),  # We lack precision when re-creating the Python float from float32.
        ("DoubleArrayValue", "DOUBLE", np.array([3.14, 0.5], dtype=np.float64)),
        ("StringArrayValue", "STRING", np.array(["Hello world! ✓", "Goodbye"], dtype=np.dtype('U'))),
    ],
)
def test_mapparametervalue_to_datatypevalue__specific_1d_array_types(japc_mock, cern, simple_value_type, expected_type_name, value):
    japc_value = cern.japc.value.spi.value
    jvalue = getattr(japc_value.simple, simple_value_type)(value)

    mpv = japc_mock.mpv(['a_name'], [jvalue])
    result = trans.MapParameterValue_to_DataTypeValue(mpv)
    assert isinstance(result, model.DataTypeValue)
    assert 'a_name' in result
    expected_type = getattr(model.BasicType, expected_type_name)
    assert result.get_type('a_name') == expected_type
    numpy.testing.assert_array_equal(result['a_name'], value)


@pytest.mark.parametrize(
    ["simple_value_type", "expected_type_name", "value"],
    [
        ("BooleanArrayValue", "BOOL", np.array([[True, False], [False, True]], dtype=np.bool)),
        ("ByteArrayValue", "INT8", np.array([[127, 0, 1], [1, 1, -3]], dtype=np.int8)),
        ("ShortArrayValue", "INT16", np.array([[135, 234, 7], [5, 1, 2]], dtype=np.int16)),
        ("IntArrayValue", "INT32", np.array([[135, 234, 7], [6, 1, 2]], dtype=np.int32)),
        ("LongArrayValue", "INT64", np.array([[135, 234, 4], [7, 1, 2]], dtype=np.int64)),
        ("FloatArrayValue", "FLOAT", np.array([[3.140000104904175, 0.5, 1.6], [7.5, 1.0, 1.1]], dtype=np.float32)),  # We lack precision when re-creating the Python float from float32.
        ("DoubleArrayValue", "DOUBLE", np.array([[3.14, 0.5, 788.6], [1.0, 34.56, 1.1]], dtype=np.float64)),
        ("StringArrayValue", "STRING", np.array([["Hello world! ✓", "Goodbye", "Goodbye2"], ["three", "four", "five"]], dtype=np.dtype('U'))),
    ],
)
def test_mapparametervalue_to_datatypevalue__specific_2d_array_types(japc_mock, cern, simple_value_type, expected_type_name, value):
    japc_value = cern.japc.value.spi.value
    jvalue = getattr(japc_value.simple, simple_value_type)(value.flatten(), value.shape)

    mpv = japc_mock.mpv(['a_name'], [jvalue])
    result = trans.MapParameterValue_to_DataTypeValue(mpv)
    assert isinstance(result, model.DataTypeValue)
    assert 'a_name' in result
    expected_type = getattr(model.BasicType, expected_type_name)
    assert result.get_type('a_name') == expected_type
    numpy.testing.assert_array_equal(result['a_name'], value)


def test_datatypevalue_mapparametervalue__multiple_values(datatype, cern):
    datatype.create_basic_item("value", model.BasicType.INT64)
    datatype.create_basic_item("another", model.BasicType.BOOL)
    dtv = datatype.create_empty_value()
    dtv['value'] = np.int64(112)
    dtv['another'] = False
    result = trans.DataTypeValue_to_MapParameterValue(dtv)
    assert isinstance(result, cern.japc.value.MapParameterValue)
    assert result.size() == 2
    assert set(result.getNames()) == {'value', 'another'}
    assert result.getValueType('value') == cern.japc.value.ValueType.LONG
    assert result.get('value').getObject() == 112
    assert result.getValueType('another') == cern.japc.value.ValueType.BOOLEAN
    assert result.get('another').getObject() == False


@pytest.mark.parametrize(
    ["dsf_type", "expected_type_name", "value"],
    [
        ("BOOL", "BOOLEAN", True),
        ("INT8", "BYTE", np.int8(127)),
        ("INT16", "SHORT", np.int16(135)),
        ("INT32", "INT", np.int32(135)),
        ("INT64", "LONG", np.int64(135)),
        ("FLOAT", "FLOAT", np.float32(3.140000104904175)),  # We lack precision when re-creating the Python float from float32.
        ("DOUBLE", "DOUBLE", np.float64(3.14)),
        ("STRING", "STRING", "Hello world! ✓"),
    ],
)
def test_datatypevalue_to_mapparametervalue__specific_types(datatype, cern, dsf_type, expected_type_name, value):
    basic_type = getattr(model.BasicType, dsf_type)
    datatype.create_basic_item("a_name", basic_type)
    dtv = datatype.create_empty_value()
    dtv['a_name'] = value

    result = trans.DataTypeValue_to_MapParameterValue(dtv)
    assert isinstance(result, cern.japc.value.MapParameterValue)
    assert 'a_name' in result.getNames()
    expected_type = getattr(cern.japc.value.ValueType, expected_type_name)
    assert result.getValueType('a_name') == expected_type
    assert result.getObject('a_name') == value


@pytest.mark.parametrize(
    ["dsf_type", "expected_type_name", "value"],
    [
        ("BOOL", "BOOLEAN_ARRAY", np.array([True, False, True], dtype=np.bool)),
        ("INT8", "BYTE_ARRAY", np.array([127, 0, -3], dtype=np.int8)),
        ("INT16", "SHORT_ARRAY", np.array([135, 234], dtype=np.int16)),
        ("INT32", "INT_ARRAY", np.array([135, 234], dtype=np.int32)),
        ("INT64", "LONG_ARRAY", np.array([135, 234], dtype=np.int64)),
        ("FLOAT", "FLOAT_ARRAY", np.array([3.140000104904175, 0.5], dtype=np.float32)),  # We lack precision when re-creating the Python float from float32.
        ("DOUBLE", "DOUBLE_ARRAY", np.array([3.14, 0.5], dtype=np.float64)),
        ("STRING", "STRING_ARRAY", np.array(["Hello world! ✓", "Goodbye"], dtype=np.dtype('U'))),
    ],
)
def test_datatypevalue_to_mapparametervalue__specific_1d_array_types(datatype, cern, dsf_type, expected_type_name, value):
    basic_type = getattr(model.BasicType, dsf_type)
    datatype.create_basic_item("a_name", basic_type, rank=1)
    dtv = datatype.create_empty_value()
    dtv['a_name'] = value

    result = trans.DataTypeValue_to_MapParameterValue(dtv)
    assert isinstance(result, cern.japc.value.MapParameterValue)
    assert 'a_name' in result.getNames()
    expected_type = getattr(cern.japc.value.ValueType, expected_type_name)
    assert result.getValueType('a_name') == expected_type
    numpy.testing.assert_array_equal(result.getObject('a_name'), value)


@pytest.mark.parametrize(
    ["dsf_type", "expected_type_name", "value"],
    [
        ("BOOL", "BOOLEAN_ARRAY_2D", np.array([[True, False], [False, True]], dtype=np.bool)),
        ("INT8", "BYTE_ARRAY_2D", np.array([[127, 0, 1], [1, 1, -3]], dtype=np.int8)),
        ("INT16", "SHORT_ARRAY_2D", np.array([[135, 234, 7], [5, 1, 2]], dtype=np.int16)),
        ("INT32", "INT_ARRAY_2D", np.array([[135, 234, 7], [6, 1, 2]], dtype=np.int32)),
        ("INT64", "LONG_ARRAY_2D", np.array([[135, 234, 4], [7, 1, 2]], dtype=np.int64)),
        ("FLOAT", "FLOAT_ARRAY_2D", np.array([[3.140000104904175, 0.5, 1.6], [7.5, 1.0, 1.1]], dtype=np.float32)),  # We lack precision when re-creating the Python float from float32.
        ("DOUBLE", "DOUBLE_ARRAY_2D", np.array([[3.14, 0.5, 788.6], [1.0, 34.56, 1.1]], dtype=np.float64)),
        ("STRING", "STRING_ARRAY_2D", np.array([["Hello world! ✓", "Goodbye", "Goodbye2"], ["three", "four", "five"]], dtype=np.dtype('U'))),
    ],
)
def test_datatypevalue_to_mapparametervalue__specific_2d_array_types(datatype, cern, dsf_type, expected_type_name, value):
    basic_type = getattr(model.BasicType, dsf_type)
    datatype.create_basic_item("a_name", basic_type, rank=2)
    dtv = datatype.create_empty_value()
    dtv['a_name'] = value

    result = trans.DataTypeValue_to_MapParameterValue(dtv)
    assert isinstance(result, cern.japc.value.MapParameterValue)
    assert 'a_name' in result.getNames()
    expected_type = getattr(cern.japc.value.ValueType, expected_type_name)
    assert result.getValueType('a_name') == expected_type
    arr2d = result.getObject('a_name')
    recorded_arr = np.array(arr2d.getArray1D(), dtype=value.dtype).reshape(arr2d.getRowCount(), arr2d.getColumnCount())
    numpy.testing.assert_array_equal(recorded_arr, value)


@pytest.mark.parametrize(
    ["selector"],
    [
        ('some.selector.here', ),
        ('', ),
    ],
)
def test_valueheader_to_context__SettingImmediateUpdateHeader(cern, selector):
    vhf = cern.japc.core.factory.ValueHeaderFactory
    header = vhf.newSettingImmediateUpdateHeader(selector)

    ctx, notification_type = trans.ValueHeader_to_ctx_notif_pair(header)
    assert isinstance(ctx, model.SettingContext)
    assert notification_type == 'SETTING_UPDATE'
    if selector:
        assert ctx.selector == selector
    else:
        # A context with a "no selector" raises an attribute error when you
        # try to access it. This may or may not be the behaviour we want.
        with pytest.raises(AttributeError):
            ctx.selector


def test_valueheader_to_context__SettingFirstUpdateHeader(cern):
    vhf = cern.japc.core.factory.ValueHeaderFactory
    header = vhf.newSettingFirstUpdateHeader(21312, 13, 'some.selector.here')
    ctx, notification_type = trans.ValueHeader_to_ctx_notif_pair(header)
    assert isinstance(ctx, model.SettingContext)
    assert notification_type == 'FIRST_UPDATE'


def test_valueheader_to_context__SettingImmediateFirstUpdateHeader_cycle_bound_no_set(cern):
    vhf = cern.japc.core.factory.ValueHeaderFactory
    header = vhf.newSettingImmediateUpdateHeader(21312, 1322313, 'some.selector.here')
    ctx, notification_type = trans.ValueHeader_to_ctx_notif_pair(header)
    assert isinstance(ctx, model.MultiplexedSettingContext)
    assert notification_type == 'SETTING_UPDATE'
    assert ctx.selector == 'some.selector.here'
    assert ctx.set_stamp == 1322313
    assert ctx.acquisition_stamp == 21312


def test_valueheader_to_context__AcquisitionRegularUpdateHeader_cycle_bound(cern):
    vhf = cern.japc.core.factory.ValueHeaderFactory
    header = vhf.newAcquisitionRegularUpdateHeader(21312, 123, 'some.selector.here')
    ctx, notification_type = trans.ValueHeader_to_ctx_notif_pair(header)
    assert isinstance(ctx, model.CycleBoundAcquisitionContext)
    assert notification_type == 'SETTING_UPDATE'
    assert ctx.cycle_stamp == 123


def test_valueheader_to_context__AcquisitionRegularUpdateHeader_cycle_bound_no_set_stamp(cern):
    vhf = cern.japc.core.factory.ValueHeaderFactory
    header = vhf.newAcquisitionRegularUpdateHeader(21312, 0, 'some.selector.here')
    ctx, notification_type = trans.ValueHeader_to_ctx_notif_pair(header)
    assert isinstance(ctx, model.AcquisitionContext)
    assert notification_type == 'SETTING_UPDATE'


def test_acqvalue_to_property_data(cern, japc_mock: "cern.japc.ext.mockito.JapcMock"):
    vhf = cern.japc.core.factory.ValueHeaderFactory

    param = japc_mock.mockParameter('ff')
    header = vhf.newAcquisitionRegularUpdateHeader(21312, 0, 'some.selector.here')
    j_acq = japc_mock.apv(param, header, 123)

    acq, notification_type = trans.AcquiredParameterValue_to_AcquiredPropertyData_notif_pair(j_acq)
    assert isinstance(acq, pyda.data.AcquiredPropertyData)
    assert acq['value'] == 123
    assert acq.header.acquisition_timestamp == 21312
    assert acq.header.selector == pyda.data.Selector('some.selector.here')
    # TODO: This is not true, must be SERVER_UPDATE, but needs another conversion fix
    assert notification_type == 'SETTING_UPDATE'
