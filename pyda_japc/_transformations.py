import typing
import pyds_model._ds_model as s


if typing.TYPE_CHECKING:
    import jpype as jp
    cern = jp.JPackage('cern')



def SimpleParameterValue_to_BasicType(param_value: "cern.japc.value.SimpleParameterValue") -> None:
    import jpype as jp

    cern = jp.JPackage('cern')

    # Perhaps this shouldn't exist... it is "field value", for which no DSF concept exists.
    s.DataType.create()
    return None


def MapParameterValue_to_DataType(param_value: "cern.japc.value.SimpleParameterValue") -> None:
    s.DataType.create()
    return None