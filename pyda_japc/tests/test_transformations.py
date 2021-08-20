import jpype as jp
import pyds_model._ds_model as _ds_model  # TODO: No private access.
import pytest

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
    assert result.entry_names() == {'a_byte', 'a_short'}
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
    assert result.contains('a_name')
    expected_type = getattr(_ds_model.BasicType, expected_type_name)
    assert result.get_type('a_name') == expected_type
    assert result['a_name'] == value

