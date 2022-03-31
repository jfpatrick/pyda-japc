import pyda_japc
import pytest
import pyrbac
import jpype as jp


@pytest.fixture
def token_bytes():

    def _wrapper(username: str) -> bytes:
        # username just to be sure that we're actually getting
        # different payload in different tests...

        # bytes by pyrbac tests (in order to create a valid token):
        # https://gitlab.cern.ch/acc-co/cmw/cmw-core/-/blob/develop/cmw-rbac-py/pyrbac/tests/test_token.py#L11
        return (b'14\n'
                b'ApplicationName\nstring\n16\nRbacAuthenticate\n'
                b'UserName\nstring\n8\nusername\n'
                b'LocationAuthReq\nbool\nfalse\n'
                b'AuthenticationTime\nint\n1617183923\n'
                b'Roles\nstring_array\n6'
                b'\nRBA%2DEGROUP%2DTEST'
                b'\nCCS%2DRBAC%2DEDITOR'
                b'\nRBA%2DDeveloper'
                b'\nRBA%2DTestRole'
                b'\nTestBed%2DUser'
                b'\nCMW%2DADMIN\n'
                b'ExpirationTime\nint\n1617212723\n'
                b'UserEmail\nstring\n17\nrba%2Eguest@cern%2Ech\n'
                b'LocationName\nstring\n13\nTESTBED%2DHOSTS\n'
                b'UserAccountType\nstring\n7\nService\n'
                b'ApplicationCritical\nbool\nfalse\n'
                b'ApplicationTimeout\nint\n-1\n'
                b'LocationAddress\nbyte_array\n4\nBCB976A2\n'
                b'SerialId\nint\n1320378323\n'
                b'UserFullName\nstring\n10\nRBAC%20GUEST\n'
                b'4\x89T@\x7f\x9f}\x96\x00|\x12\x98Dmb\x06e'
                b'\xfa\x17\xee[\x12-\xcf:\x18\xce\xb7\x998'
                b'\x1a+.u=\xe6\xe2\x03ne\x92\x0e}\x0e\x86'
                b'\xabY\xdc\xb7\xb0\xe6\x1es\xb4\xe9^R"\x84'
                b'\xdc\xe2E\x99E\xedHuJR\xc7\x87f/s/5\xac\x85'
                b'\xe7Zh\xa5-\xae\xdb|G3\xf5\x1d3"P\xe9\x82'
                b'\xbc\x85\xf9X\xbb\x03\xd4\x13\xabC@0=\x9eb'
                b'\xb7;\x85\x87{qoJA\xdes\x17Gv\xeat\x87\x97'
                b'\x95\x97\xd3\xd7\x8b\xc5v\xb9n\xc9\xbb\x10'
                b'\xe6#O\xd84\x0c7t\x8d&\xad\xebz\xf8\xa1\xa6'
                b'\xcb\xbe\xec\x926\xf3\xfaU\xd4#W_vX\xbd\xe3y'
                b'\x9a^\x1e+|sf\xf4\xe6ZE+\xf1_\xa0\xce\x03\xf3'
                b'\xca\xbcRi\xebR-!\xc7.\x1d\xb2\x18)\x80\xd6l'
                b'\xb9\xcc5\xb1]\x88|~}\x84EO\xdb\x1e\xcb\xe0S'
                b'\x02\x00_\xbb\xab\x1a\xfaU?\xc2\xdb\xf1\x8aS6'
                b'\x87\xbe\x137{63\xe5\x05\xfaw\xf0x3\xc7\x13'
                b'\x00\x01\x00\x00')

    return _wrapper


@pytest.mark.skip('Creation of pyrbac token with bytes above does not produce a valid token')
@pytest.mark.parametrize('convert_to_token', [True, False])
def test_sets_token_initially(token_bytes, convert_to_token, jvm):
    token_arg = buffer = token_bytes("User1")
    if convert_to_token:
        token_arg = pyrbac.Token(token_arg)
    provider = pyda_japc.JapcProvider(rbac_token=token_arg)
    assert provider.rbac_token.get_encoded() == buffer


def test_sets_empty_token_initially():
    provider = pyda_japc.JapcProvider(rbac_token=pyrbac.Token.create_empty_token())
    assert provider.rbac_token is not None
    assert provider.rbac_token.empty()


@pytest.mark.skip('Creation of pyrbac token with bytes above does not produce a valid token')
@pytest.mark.parametrize('convert_to_token', [True, False])
def test_sets_token_after_creation(token_bytes, convert_to_token, jvm):
    token_arg = buffer = token_bytes("User2")
    if convert_to_token:
        token_arg = pyrbac.Token(token_arg)
    provider = pyda_japc.JapcProvider()
    assert provider.rbac_token is None
    provider.rbac_token = token_arg
    assert provider.rbac_token.get_encoded() == buffer


def test_sets_empty_token_after_creation():
    provider = pyda_japc.JapcProvider()
    assert provider.rbac_token is None
    provider.rbac_token = pyrbac.Token.create_empty_token()
    assert provider.rbac_token is not None
    assert provider.rbac_token.empty()


@pytest.mark.skip('Creation of pyrbac token with bytes above does not produce a valid token')
def test_reflects_preexisting_token(token_bytes, cern):
    buffer = token_bytes("User3")
    buffer_j = jp.java.nio.ByteBuffer.wrap(buffer)
    token_j = cern.rbac.common.RbaToken.parseAndValidate(buffer_j)
    cern.rbac.util.holder.ClientTierTokenHolder.setRbaToken(token_j)
    provider = pyda_japc.JapcProvider()
    assert provider.rbac_token is not None
    assert provider.rbac_token.get_encoded() == buffer
