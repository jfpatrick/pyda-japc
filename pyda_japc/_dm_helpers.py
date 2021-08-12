from pyds_model import _ds_model

from pyds_model._ds_model import BasicType as _bt


_TYPE_TO_NAME = {
    _bt.STRING: "str",
    _bt.BOOL: "bool",

    _bt.FLOAT: "float",
    _bt.DOUBLE: "double",

    _bt.INT8: "int8",
    _bt.INT16: "int16",
    _bt.INT32: "int32",
    _bt.INT64: "int64",

    _bt.UINT8: "uint8",
    _bt.UINT16: "uint16",
    _bt.UINT32: "uint32",
    _bt.UINT64: "uint64",
}


def _type_to_method_suffix(basic_type: _ds_model.BasicType, array_rank=0):
    if array_rank not in [0, 1, 2]:
        raise ValueError("Array rank must be 0, 1 or 2")

    if basic_type not in _TYPE_TO_NAME:
        raise TypeError(f"Unhandled type {basic_type}")
    if array_rank == 0:
        rank_suffix = ''
    elif array_rank == 1:
        rank_suffix = '_array'
    elif array_rank == 2:
        rank_suffix = '_array_2D'

    return f'{_TYPE_TO_NAME[basic_type]}{rank_suffix}'


def getter_for_type(data: _ds_model.AnyData, basic_type: _ds_model.BasicType, array_rank=0):
    """Return the method for getting data of the given type."""
    getter_name = f'get_{_type_to_method_suffix(basic_type, array_rank)}'
    return getattr(data, getter_name)


def setter_for_type(data: _ds_model.AnyData, basic_type: _ds_model.BasicType, array_rank=0):
    """Return the method for setting data of the given type."""
    getter_name = f'set_{_type_to_method_suffix(basic_type, array_rank)}'
    return getattr(data, getter_name)
