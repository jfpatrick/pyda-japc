import functools
import cmmnbuild_dep_manager

import jpype as jp
import numpy as np


@functools.lru_cache()
def _scalar_to_dtype_lookup():
    # NOTE: Assumes that the JVM has started.
    SCALAR_DTYPE = {
        jp.java.lang.Byte: np.int8,
        jp.java.lang.Short: np.int16,
        jp.java.lang.Integer: np.int32,
        jp.java.lang.Long: np.int64,
        jp.java.lang.Float: np.float32,
        jp.java.lang.Double: np.float64,
        jp.java.lang.Boolean: bool,
        jp.java.lang.String: str,
    }
    return SCALAR_DTYPE


def jscalar_to_scalar(scalar_value: jp.JObject) -> np.ndarray:
    SCALAR_TO_DTYPE = _scalar_to_dtype_lookup()
    if type(scalar_value) not in SCALAR_TO_DTYPE:
        raise TypeError(f"Cannot convert Java scalar type {type(scalar_value)} to a Python scalar")
    dtype = SCALAR_TO_DTYPE[type(scalar_value)]
    return dtype(scalar_value)


@functools.lru_cache()
def cern_pkg() -> "cern":
    mgr = cmmnbuild_dep_manager.Manager()
    if not mgr.is_resolved():
        mgr.resolve()
    if not jp.isJVMStarted():
        mgr.start_jpype_jvm()
    return jp.JPackage('cern')
