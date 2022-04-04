import pyda_japc
import pytest
import pyrbac
import jpype as jp


@pytest.fixture(scope='function', autouse=True)
def clear_rbac_token_from_java(cern):
    try:
        yield
    finally:
        cern.rbac.util.holder.ClientTierTokenHolder.clear()


@pytest.fixture
def token_bytes():
    # No currently nice way to generate different tokens with arbitrary usernames
    # cern.rbac.common.test.TestTokenBuilder would be a great solution, except
    # it uses randomly generated key-value pair, while the system under test
    # will always use PRO keys (or defined by RBAC_ENV), so validation will never
    # pass
    return b'14\n' \
           b'ApplicationName\nstring\n16\nRbacAuthenticate\n' \
           b'UserName\nstring\n8\nrbaguest\n' \
           b'LocationAuthReq\nbool\nfalse\n' \
           b'AuthenticationTime\nint\n1648828262\n' \
           b'Roles\nstring_array\n3' \
           b'\nRBA%2DDeveloper' \
           b'\nCCS%2DRBAC%2DEDITOR' \
           b'\nRBA%2DTestRole\n' \
           b'ExpirationTime\nint\n1648857062\n' \
           b'UserEmail\nstring\n17\nrba%2Eguest@cern%2Ech\n' \
           b'LocationName\nstring\n11\nVM%2DISINKARE\n' \
           b'UserAccountType\nstring\n7\nService\n' \
           b'ApplicationCritical\nbool\nfalse\n' \
           b'ApplicationTimeout\nint\n-1\n' \
           b'LocationAddress\nbyte_array\n4\nBCB9718B\n' \
           b'SerialId\nint\n367757248\n' \
           b'UserFullName\nstring\n10\nRBAC%20GUEST\n' \
           b'C\x07\xa8Z\x06$\xd6\x8d?\xc0\xf8\x817\x87\xbc\xab' \
           b'\xba\xaa\xf0.&\xf9\xb0\xd8-:\xbeN=\xc1y\xc5\xdf\x06' \
           b'\x86\xd5\x00M\n\x1b\\\r<\xfa-\xe6\xcc\xdb\x7fef' \
           b'\x8eP\xd5\x1c\xbb\x85\xd7\x88\xc1M\xfb\xd02@\x00\x00\x00'


@pytest.mark.parametrize('convert_to_token', [True, False])
def test_sets_token_initially(token_bytes, convert_to_token, cern):
    token_arg = token_bytes
    if convert_to_token:
        token_arg = pyrbac.Token(token_arg)
    provider = pyda_japc.JapcProvider(rbac_token=token_arg)
    assert provider.rbac_token.get_encoded() == token_bytes
    assert provider.rbac_token.get_user_name() == "rbaguest"


def test_sets_empty_token_initially(jvm):
    provider = pyda_japc.JapcProvider(rbac_token=pyrbac.Token.create_empty_token())
    assert provider.rbac_token is not None
    assert provider.rbac_token.empty()


@pytest.mark.parametrize('convert_to_token', [True, False])
def test_sets_token_after_creation(token_bytes, convert_to_token, jvm):
    token_arg = token_bytes
    if convert_to_token:
        token_arg = pyrbac.Token(token_arg)
    provider = pyda_japc.JapcProvider()
    assert provider.rbac_token is None
    provider.rbac_token = token_arg
    assert provider.rbac_token.get_encoded() == token_bytes
    assert provider.rbac_token.get_user_name() == "rbaguest"


def test_sets_empty_token_after_creation(jvm):
    provider = pyda_japc.JapcProvider()
    assert provider.rbac_token is None
    provider.rbac_token = pyrbac.Token.create_empty_token()
    assert provider.rbac_token is not None
    assert provider.rbac_token.empty()


def test_reflects_preexisting_token(token_bytes, cern):
    buffer_j = jp.java.nio.ByteBuffer.wrap(token_bytes)
    token_j = cern.rbac.common.RbaToken.parseNoValidate(buffer_j)
    cern.rbac.util.holder.ClientTierTokenHolder.setRbaToken(token_j)
    provider = pyda_japc.JapcProvider()
    assert provider.rbac_token is not None
    assert provider.rbac_token.get_encoded() == token_bytes
    assert provider.rbac_token.get_user_name() == "rbaguest"


def test_getter_token_reflects_java(cern, token_bytes):
    provider = pyda_japc.JapcProvider(rbac_token=token_bytes)
    bytes_j = cern.rbac.util.holder.ClientTierTokenHolder.getRbaToken().getEncoded()
    assert provider.rbac_token.get_encoded() == bytes(bytes_j)
    # Check that original token has not been affected
    assert cern.rbac.util.holder.ClientTierTokenHolder.getRbaToken().getUser().getName() == "rbaguest"


def test_sets_initializing_with_none_token_clears_java(token_bytes, cern):
    buffer_j = jp.java.nio.ByteBuffer.wrap(token_bytes)
    token_j = cern.rbac.common.RbaToken.parseNoValidate(buffer_j)
    cern.rbac.util.holder.ClientTierTokenHolder.setRbaToken(token_j)
    assert cern.rbac.util.holder.ClientTierTokenHolder.getRbaToken().getUser().getName() == "rbaguest"
    _ = pyda_japc.JapcProvider(rbac_token=None)
    assert cern.rbac.util.holder.ClientTierTokenHolder.getRbaToken() is None
