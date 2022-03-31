import pyda_japc
import pytest
import pyrbac
import jpype as jp


# @pytest.mark.skip('Creation of pyrbac token with bytes above does not produce a valid token')
# @pytest.mark.parametrize('convert_to_token', [True, False])
# def test_sets_token_initially(token_bytes, convert_to_token, jvm):
#     token_arg = buffer = token_bytes("User1")
#     if convert_to_token:
#         token_arg = pyrbac.Token(token_arg)
#     provider = pyda_japc.JapcProvider(rbac_token=token_arg)
#     assert provider.rbac_token.get_encoded() == buffer


def test_sets_empty_token_initially():
    provider = pyda_japc.JapcProvider(rbac_token=pyrbac.Token.create_empty_token())
    assert provider.rbac_token is not None
    assert provider.rbac_token.empty()


# @pytest.mark.skip('Creation of pyrbac token with bytes above does not produce a valid token')
# @pytest.mark.parametrize('convert_to_token', [True, False])
# def test_sets_token_after_creation(token_bytes, convert_to_token, jvm):
#     token_arg = buffer = token_bytes("User2")
#     if convert_to_token:
#         token_arg = pyrbac.Token(token_arg)
#     provider = pyda_japc.JapcProvider()
#     assert provider.rbac_token is None
#     provider.rbac_token = token_arg
#     assert provider.rbac_token.get_encoded() == buffer


def test_sets_empty_token_after_creation():
    provider = pyda_japc.JapcProvider()
    assert provider.rbac_token is None
    provider.rbac_token = pyrbac.Token.create_empty_token()
    assert provider.rbac_token is not None
    assert provider.rbac_token.empty()


# @pytest.mark.skip('Creation of pyrbac token with bytes above does not produce a valid token')
# def test_reflects_preexisting_token(token_bytes, cern):
#     buffer = token_bytes("User3")
#     buffer_j = jp.java.nio.ByteBuffer.wrap(buffer)
#     token_j = cern.rbac.common.RbaToken.parseAndValidate(buffer_j)
#     cern.rbac.util.holder.ClientTierTokenHolder.setRbaToken(token_j)
#     provider = pyda_japc.JapcProvider()
#     assert provider.rbac_token is not None
#     assert provider.rbac_token.get_encoded() == buffer
