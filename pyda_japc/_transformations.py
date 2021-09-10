import functools
import typing
import warnings

import jpype as jp
import numpy as np
import pyds_model as model

from . import _jpype_tools


if typing.TYPE_CHECKING:
    cern = jp.JPackage("cern")


@functools.lru_cache()
def _ValueTypes_To_BasicTypes() -> typing.Dict["cern.japc.value.ValueType", model.BasicType]:
    ValueType = jp.JPackage('cern').japc.value.ValueType
    t = model.BasicType
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


@functools.lru_cache()
def _BasicTypes_to_JPype_Types() -> typing.Dict[model.BasicType, typing.Type]:
    t = model.BasicType
    return {
        t.BOOL: jp.JBoolean,

        t.INT8: jp.JByte,
        t.INT16: jp.JShort,
        t.INT32: jp.JInt,
        t.INT64: jp.JLong,

        t.FLOAT: jp.JFloat,
        t.DOUBLE: jp.JDouble,

        t.STRING: jp.JString,
    }


def ValueType_to_BasicType(value_type: "cern.japc.value.ValueType") -> model.BasicType:
    """
    Get the :class:`pyds_model.BasicType` for the given cern.japc.value.ValueType.

    Note that ValueType is not a 1-2-1 mapping of BasicType. For example,
    ValueType may contain array/rank info, whereas BasicType does not.
    """
    basic_type_lookup = _ValueTypes_To_BasicTypes()
    if value_type not in basic_type_lookup:
        raise TypeError(f"Unknown type {value_type}")
    return basic_type_lookup[value_type]


def MapParameterValue_to_DataTypeValue(param_value: "cern.japc.value.MapParameterValue") -> model.DataTypeValue:
    # Build a device class and property so that we can get hold of an empty
    # DataType instance (no better way currently).
    dc = model.DeviceClass.create('name', '0.1')
    prop = dc.create_acquisition_property('delme')
    dtype: model.DataType = prop.data_type

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
        elif isinstance(actual_value, jp.JArray):
            actual_value = np.array(actual_value)
        elif isinstance(actual_value, str):
            # JPype already converts java strings to python strings for us.
            pass
        else:
            # We need to special case scalars because of https://github.com/jpype-project/jpype/issues/997.
            actual_value = _jpype_tools.jscalar_to_scalar(actual_value)
        data[name] = actual_value
    return data


def DataTypeValue_to_MapParameterValue(dtv: model.DataTypeValue) -> "cern.japc.value.MapParameterValue":
    cern = jp.JPackage("cern")
    mpv = cern.japc.core.factory.MapParameterValueFactory.newValue()
    for name, val in dtv.items():
        basic_type = dtv.get_type(name)
        jp_type = _BasicTypes_to_JPype_Types()[basic_type]
        if isinstance(val, np.ndarray):
            jarr = jp.JArray(jp_type, 1)(val.flatten())
            if val.ndim == 1:
                spv = cern.japc.core.factory.SimpleParameterValueFactory.newValue(jarr)
            elif val.ndim == 2:
                shape = jp.JArray(jp.JInt)(val.shape)
                spv = cern.japc.core.factory.SimpleParameterValueFactory.newValue(jarr, shape)
            else:
                warnings.warn(f'Unsupported number of dimensions ({val.ndim}) in array "{name}". Won\'t be transformed.')
        else:
            jval = jp_type(val)
            spv = cern.japc.core.factory.SimpleParameterValueFactory.newValue(jval)
        mpv.put(name, spv)
    return mpv
