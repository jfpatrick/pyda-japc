import functools
import warnings

import jpype as jp
import typing
import pyds_model._ds_model as _ds_model  # TODO: Only use public classes.


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


def _getter_setter_for_type(basic_type: _ds_model.BasicType, array_rank=0):
    """
    Return the unbound methods for getting and setting to the given type on :class:`AnyData`.

    """
    t = _ds_model.BasicType
    if array_rank not in [0, 1, 2]:
        raise ValueError("Array rank must be 0, 1 or 2")
    type_to_name = {
        t.STRING: "str",
        t.BOOL: "bool",

        t.FLOAT: "float",
        t.DOUBLE: "double",

        t.INT8: "int8",
        t.INT16: "int16",
        t.INT32: "int32",
        t.INT64: "int64",

        t.UINT8: "uint8",
        t.UINT16: "uint16",
        t.UINT32: "uint32",
        t.UINT64: "uint64",
    }
    if basic_type not in type_to_name:
        raise TypeError(f"Unhandled type {basic_type}")
    if array_rank == 0:
        rank_suffix = ''
    elif array_rank == 1:
        rank_suffix = '_array'
    elif array_rank == 2:
        rank_suffix = '_array_2D'

    getter_name = f'get_{type_to_name[basic_type]}{rank_suffix}'
    setter_name = f'set_{type_to_name[basic_type]}{rank_suffix}'
    return getattr(_ds_model.AnyData, getter_name), getattr(_ds_model.AnyData, setter_name)


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
    for name in param_value.getNames():
        value: cern.japc.value.SimpleParameterValue = param_value.get(name)
        value_type = value.getValueType()

        if value_type.isArray2d():
            array_rank = 2
        elif value_type.isArray():
            array_rank = 1
        else:
            array_rank = 0
        if value_type.isArray() or value_type.isArray2d():
            # TODO: Implement this.
            warnings.warn(f'Array support not implemented for {name} (type: {value_type})')
            continue

        basic_type = ValueType_to_BasicType(value_type.getComponentType())
        actual_value = value.getObject()

        # Set the data using the correct method.
        setter = _getter_setter_for_type(basic_type, array_rank)[1]
        setter(data, name, actual_value)

    return data
