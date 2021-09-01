import functools
import warnings

import jpype
import jpype as jp
import typing

import numpy as np
import pyds_model._ds_model as _ds_model  # TODO: Only use public classes.

from . import _jpype_tools


if typing.TYPE_CHECKING:
    cern = jp.JPackage("cern")


@functools.lru_cache()
def _ValueTypes_To_BasicTypes() -> typing.Dict["cern.japc.value.ValueType", _ds_model.BasicType]:
    ValueType = jp.JPackage('cern').japc.value.ValueType
    t = _ds_model.BasicType
    return {
        ValueType.BOOLEAN: t.BOOL,

        ValueType.BYTE: t.INT8,
        ValueType.SHORT: t.INT16,
        ValueType.INT: t.INT32,
        ValueType.LONG: t.INT64,

        ValueType.FLOAT: t.FLOAT,
        ValueType.DOUBLE: t.DOUBLE,

        ValueType.STRING: t.STRING,
    }


def ValueType_to_BasicType(value_type: "cern.japc.value.ValueType") -> _ds_model.BasicType:
    """
    Get the :class:`pyds_model._ds_model.BasicType` for the given cern.japc.value.ValueType.

    Note that ValueType is not a 1-2-1 mapping of BasicType. For example,
    ValueType may contain array/rank info, whereas BasicType does not.
    """
    basic_type_lookup = _ValueTypes_To_BasicTypes()
    if value_type not in basic_type_lookup:
        raise TypeError(f"Unknown type {value_type}")
    return basic_type_lookup[value_type]


def MapParameterValue_to_DataTypeValue(param_value: "cern.japc.value.MapParameterValue") -> _ds_model.DataTypeValue:
    # Build a device class and property so that we can get hold of an empty
    # DataType instance (no better way currently).
    dc = _ds_model.DeviceClass.create('name', '0.1')
    prop = dc.create_acquisition_property('delme')
    dtype: _ds_model.DataType = prop.data_type

    # Build up the datatype based on the given MapParameterValue types.
    for name in param_value.getNames():
        value: cern.japc.value.SimpleParameterValue = param_value.get(name)
        value_type = value.getValueType()

        if value_type.isArray2d():
            array_rank = 2
        elif value_type.isArray():
            array_rank = 1
        else:
            array_rank = 0

        basic_type = ValueType_to_BasicType(value_type.getComponentType())
        dtype.create_basic_item(name, basic_type, rank=array_rank)

    # Create a DataTypeValue for the DataType we have just built-up.
    data = dtype.create_empty_value(accepts_partial=True)

    cern = jp.JPackage("cern")
    for name in param_value.getNames():
        value: cern.japc.value.SimpleParameterValue = param_value.get(name)
        actual_value = value.getObject()
        if isinstance(actual_value, cern.japc.value.Array2D):
            actual_value = np.array(actual_value.getArray1D()) \
                .reshape(actual_value.getRowCount(), actual_value.getColumnCount())
        elif isinstance(actual_value, jpype.JArray):
            actual_value = np.array(actual_value)
        elif isinstance(actual_value, str):
            # JPype already converts java strings to python strings for us.
            pass
        else:
            # We need to special case scalars because of https://github.com/jpype-project/jpype/issues/997.
            actual_value = _jpype_tools.jscalar_to_scalar(actual_value)
        data[name] = actual_value
    return data
