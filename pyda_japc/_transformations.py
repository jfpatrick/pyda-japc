import functools

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
