import jpype as jp
import pyds_model._ds_model as _ds_model  # TODO: No private access.
import pyda_japc._transformations as trans
import pytest


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
