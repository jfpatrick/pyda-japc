"""
High-level tests for the  package.

"""

import pyda_japc
import jpype as jp
import cmmnbuild_dep_manager as c

import pytest


@pytest.fixture
def jvm():
    
    c.Manager().start_jpype_jvm()


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
    # v = japc_value.IntValue(32)
    
    print(v.)
    assert str(v) == 'asdasd'




