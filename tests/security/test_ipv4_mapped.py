from TARS.security.network import validate_url_target


def test_ipv4_mapped_ipv6():
    import socket
    from unittest.mock import patch
    def _resolver(hostname, port, family=0, type_=0):
        return [(socket.AF_INET6, socket.SOCK_STREAM, 0, "", ("::ffff:127.0.0.1", 0, 0, 0))]
    with patch("TARS.security.network.socket.getaddrinfo", _resolver):
        ok, err = validate_url_target("http://evil.com/")
        assert not ok, "IPv4-mapped loopback should be blocked"
