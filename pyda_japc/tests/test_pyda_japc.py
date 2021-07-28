"""
High-level tests for the pyds-japc package.

"""

import pyda_japc
import jpype as jp

import pytest

import pyds_model._ds_model as _ds_model


def test_ds_model_works():
    # TODO: This test can be removed once we are using the module
    #  in our tests.
    assert _ds_model.BasicType is not None


@pytest.fixture
def japc_value(jvm):
    _ = jvm
    
    cern = jp.JPackage('cern')
    return cern.japc.value


def test_version():
    assert pyda_japc.__version__ is not None


def test_value_descriptor(japc_value):
    SimpleParameterValueFactory = jp.JClass(
        "cern.japc.core.factory.SimpleParameterValueFactory")
    v = SimpleParameterValueFactory.newSimpleParameterValue(jp.JInt(32))

    # TODO: This test can be removed once we are using JAPC properly.
    assert str(v) == '(int:1) -> 32'
