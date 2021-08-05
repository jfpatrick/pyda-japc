"""
High-level tests for the pyds-japc package.

"""

import pyda_japc
import jpype as jp

import pytest


def test_version():
    assert pyda_japc.__version__ is not None
