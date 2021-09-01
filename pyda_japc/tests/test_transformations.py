import jpype as jp
import pyds_model._ds_model as _ds_model  # TODO: No private access.
import pytest
import numpy as np
import numpy.testing

import pyda_japc._transformations as trans


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
def test_value_type_to_basic_type(jvm, input_type_name, output_type_name):
    ValueType = jp.JPackage("cern").japc.value.ValueType
    input_type = getattr(ValueType, input_type_name)
    output_type = getattr(_ds_model.BasicType, output_type_name)
    assert trans.ValueType_to_BasicType(input_type) == output_type


def test_value_type_to_basic_type_missing(jvm):
    with pytest.raises(TypeError, match='Unknown type None'):
        trans.ValueType_to_BasicType(None)


def test_mapparametervalue_to_datatypevalue_multiple_values(japc_mock):
    japc_value = jp.JPackage("cern").japc.value.spi.value
    mpv = japc_mock.mpv(
        ['a_byte', 'a_short'], [
            japc_value.simple.ByteValue(127),
            japc_value.simple.ShortValue(2),
        ]
    )
    result = trans.MapParameterValue_to_DataTypeValue(mpv)
    assert isinstance(result, _ds_model.DataTypeValue)
    assert result.keys() == {'a_byte', 'a_short'}
    assert result.get_type('a_byte') == _ds_model.BasicType.INT8
    assert result['a_byte'] == 127
    assert result.get_type('a_short') == _ds_model.BasicType.INT16
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
def test_mapparametervalue_to_datatypevalue__specific_types(japc_mock, simple_value_type, expected_type_name, value):
    japc_value = jp.JPackage("cern").japc.value.spi.value
    jvalue = getattr(japc_value.simple, simple_value_type)(value)

    mpv = japc_mock.mpv(['a_name'], [jvalue])
    result = trans.MapParameterValue_to_DataTypeValue(mpv)
    assert isinstance(result, _ds_model.DataTypeValue)
    assert 'a_name' in result
    expected_type = getattr(_ds_model.BasicType, expected_type_name)
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
def test_mapparametervalue_to_datatypevalue__specific_1d_array_types(japc_mock, simple_value_type, expected_type_name, value):
    japc_value = jp.JPackage("cern").japc.value.spi.value
    jvalue = getattr(japc_value.simple, simple_value_type)(value)

    mpv = japc_mock.mpv(['a_name'], [jvalue])
    result = trans.MapParameterValue_to_DataTypeValue(mpv)
    assert isinstance(result, _ds_model.DataTypeValue)
    assert 'a_name' in result
    expected_type = getattr(_ds_model.BasicType, expected_type_name)
    assert result.get_type('a_name') == expected_type
    numpy.testing.assert_array_equal(result['a_name'], value)


@pytest.mark.parametrize(
    ["simple_value_type", "expected_type_name", "value"],
    [
        ("BooleanArrayValue", "BOOL", np.array([[True, False], [False, True]], dtype=np.bool)),
        ("ByteArrayValue", "INT8", np.array([[127, 0], [1, -3]], dtype=np.int8)),
        ("ShortArrayValue", "INT16", np.array([[135, 234], [1, 2]], dtype=np.int16)),
        ("IntArrayValue", "INT32", np.array([[135, 234], [1, 2]], dtype=np.int32)),
        ("LongArrayValue", "INT64", np.array([[135, 234], [1, 2]], dtype=np.int64)),
        ("FloatArrayValue", "FLOAT", np.array([[3.140000104904175, 0.5], [1.0, 1.1]], dtype=np.float32)),  # We lack precision when re-creating the Python float from float32.
        ("DoubleArrayValue", "DOUBLE", np.array([[3.14, 0.5], [1.0, 1.1]], dtype=np.float64)),
        ("StringArrayValue", "STRING", np.array([["Hello world! ✓", "Goodbye"], ["three", "four"]], dtype=np.dtype('U'))),
    ],
)
def test_mapparametervalue_to_datatypevalue__specific_2d_array_types(japc_mock, simple_value_type, expected_type_name, value):
    japc_value = jp.JPackage("cern").japc.value.spi.value
    jvalue = getattr(japc_value.simple, simple_value_type)(value.flatten(), value.shape)

    mpv = japc_mock.mpv(['a_name'], [jvalue])
    result = trans.MapParameterValue_to_DataTypeValue(mpv)
    assert isinstance(result, _ds_model.DataTypeValue)
    assert 'a_name' in result
    expected_type = getattr(_ds_model.BasicType, expected_type_name)
    assert result.get_type('a_name') == expected_type
    numpy.testing.assert_array_equal(result['a_name'], value)
