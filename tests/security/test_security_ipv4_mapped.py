from TARS.security.network import _is_private
import ipaddress

def test_ipv4_mapped_ipv6():
    assert _is_private(ipaddress.ip_address("::ffff:127.0.0.1"))
    assert _is_private(ipaddress.ip_address("::ffff:10.0.0.1"))
    assert not _is_private(ipaddress.ip_address("::ffff:8.8.8.8"))
