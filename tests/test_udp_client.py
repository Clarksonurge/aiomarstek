"""Tests for the Marstek UDP client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from aiomarstek import MarstekUDPClient


@pytest.fixture
def socket_mock() -> MagicMock:
    """Mock Marstek UDP sockets."""
    socket_instance = MagicMock()
    socket_instance.getsockname.return_value = ("0.0.0.0", 30000)
    with patch("aiomarstek.udp_client._SOCKET_FACTORY", return_value=socket_instance):
        yield socket_instance


async def test_async_setup(socket_mock: MagicMock) -> None:
    """Test UDP client setup."""
    client = MarstekUDPClient()

    await client.async_setup()

    socket_mock.setsockopt.assert_called()
    socket_mock.setblocking.assert_called_once_with(False)
    socket_mock.bind.assert_called_once_with(("0.0.0.0", 30000))


async def test_async_cleanup(socket_mock: MagicMock) -> None:
    """Test UDP client cleanup."""
    client = MarstekUDPClient()

    await client.async_setup()
    await client.async_cleanup()

    socket_mock.close.assert_called_once()


async def test_send_udp_message(socket_mock: MagicMock) -> None:
    """Test sending UDP messages."""
    client = MarstekUDPClient()

    await client._send_udp_message('{"id": 1, "method": "test"}', "192.0.2.1", 30000)

    socket_mock.sendto.assert_called_once_with(
        b'{"id": 1, "method": "test"}',
        ("192.0.2.1", 30000),
    )


async def test_discover_devices_cache(socket_mock: MagicMock) -> None:
    """Test device discovery cache."""
    client = MarstekUDPClient()
    response = {
        "id": 1,
        "result": {
            "id": 0,
            "device": "ES5",
            "ver": 1,
            "wifi_name": "TestWiFi",
            "ip": "192.0.2.1",
            "wifi_mac": "AA:BB:CC:DD:EE:FF",
            "ble_mac": "11:22:33:44:55:66",
        },
    }

    with patch.object(client, "send_broadcast_request", return_value=[response]):
        devices = await client.discover_devices(use_cache=False)
        cached_devices = await client.discover_devices(use_cache=True)

    assert devices == cached_devices
    assert cached_devices[0]["device_type"] == "ES5"
    assert cached_devices[0]["ip"] == "192.0.2.1"


async def test_polling_control() -> None:
    """Test polling pause and resume."""
    client = MarstekUDPClient()

    assert not client.is_polling_paused("192.0.2.1")
    await client.pause_polling("192.0.2.1")
    assert client.is_polling_paused("192.0.2.1")
    await client.resume_polling("192.0.2.1")
    assert not client.is_polling_paused("192.0.2.1")


async def test_send_request_invalid_message(socket_mock: MagicMock) -> None:
    """Test invalid request payload handling."""
    client = MarstekUDPClient()

    with pytest.raises(ValueError):
        await client.send_request("not json", "192.0.2.1", timeout=0.1)


async def test_get_device_status_preserves_previous_data() -> None:
    """Test status helper preserves previous data when requests fail."""
    client = MarstekUDPClient()
    previous_data = {"battery_soc": 42, "pv1_power": 100}

    with patch.object(client, "send_request", side_effect=TimeoutError):
        result = await client.get_device_status(
            "192.0.2.1",
            previous_data=previous_data,
            delay_ms=0,
        )

    assert result["battery_soc"] == 42
    assert result["pv1_power"] == 100
    assert result["device_ip"] == "192.0.2.1"
