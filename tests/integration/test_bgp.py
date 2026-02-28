import pytest
import shlex
import time


@pytest.mark.parametrize(
    "commands, expected",
    [
        # Test peering-address only (IPv4)
        (
            ["peering-address 192.0.2.1"],
            {
                "bgp.peering-addr": "192.0.2.1",
            },
        ),
        # Test peering-address only (IPv6)
        (
            ["peering-address fd00::1"],
            {
                "bgp.peering-addr": "fd00::1",
            },
        ),
        # Test peering-address with afi-safi
        (
            ["peering-address 192.0.2.1 afi-safi ipv4-unicast,ipv6-unicast"],
            {
                "bgp.peering-addr": "192.0.2.1",
                "bgp.afi-safi": "ipv4-unicast,ipv6-unicast",
            },
        ),
        # Test peering-address IPv6 with afi-safi
        (
            ["peering-address fd00::1 afi-safi ipv6-unicast"],
            {
                "bgp.peering-addr": "fd00::1",
                "bgp.afi-safi": "ipv6-unicast",
            },
        ),
        # Test router-id
        (
            ["router-id 10.0.0.1", "peering-address 192.0.2.1"],
            {
                "bgp.router-id": "10.0.0.1",
                "bgp.peering-addr": "192.0.2.1",
            },
        ),
        # Test as-number
        (
            ["as-number 65000", "peering-address 192.0.2.1"],
            {
                "bgp.as": "65000",
                "bgp.peering-addr": "192.0.2.1",
            },
        ),
        # Test full configuration
        (
            [
                "router-id 10.0.0.1",
                "as-number 65001",
                "peering-address fd00::1 afi-safi ipv4-unicast,ipv6-unicast",
            ],
            {
                "bgp.router-id": "10.0.0.1",
                "bgp.as": "65001",
                "bgp.peering-addr": "fd00::1",
                "bgp.afi-safi": "ipv4-unicast,ipv6-unicast",
            },
        ),
    ],
)
def test_bgp_config(lldpd1, lldpd, lldpcli, namespaces, commands, expected):
    """Test BGP peer discovery TLV configuration and neighbor advertisement."""
    with namespaces(2):
        lldpd()
        for command in commands:
            result = lldpcli(*shlex.split("configure lldp bgp-config {}".format(command)))
            assert result.returncode == 0
        time.sleep(3)
    with namespaces(1):
        pfx = "lldp.eth0.bgp."
        out = lldpcli("-f", "keyvalue", "show", "neighbors", "details")
        out = {k[len(pfx):]: v for k, v in out.items() if k.startswith(pfx)}
        assert out == expected
