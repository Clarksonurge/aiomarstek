"""Tests for the Marstek command builder."""

from __future__ import annotations

import json

from aiomarstek import (
    CMD_BATTERY_STATUS,
    CMD_DISCOVER,
    CMD_ES_MODE,
    CMD_ES_STATUS,
    CMD_PV_GET_STATUS,
    build_command,
    discover,
    get_battery_status,
    get_es_mode,
    get_es_status,
    get_next_request_id,
    get_pv_status,
    reset_request_id,
)


def test_get_next_request_id() -> None:
    """Test request ID generation."""
    reset_request_id()
    assert get_next_request_id() == 1
    assert get_next_request_id() == 2
    assert get_next_request_id() == 3


def test_reset_request_id() -> None:
    """Test request ID reset."""
    get_next_request_id()
    get_next_request_id()
    reset_request_id()
    assert get_next_request_id() == 1


def test_build_command() -> None:
    """Test building a command."""
    reset_request_id()
    command = build_command("test.method", {"param": "value"})
    parsed = json.loads(command)

    assert parsed["id"] == 1
    assert parsed["method"] == "test.method"
    assert parsed["params"] == {"param": "value"}


def test_build_command_without_params() -> None:
    """Test building a command without parameters."""
    reset_request_id()
    command = build_command("test.method")
    parsed = json.loads(command)

    assert parsed["id"] == 1
    assert parsed["method"] == "test.method"
    assert parsed["params"] == {}


def test_discover() -> None:
    """Test discover command."""
    reset_request_id()
    command = discover()
    parsed = json.loads(command)

    assert parsed["id"] == 1
    assert parsed["method"] == CMD_DISCOVER
    assert parsed["params"] == {"ble_mac": "0"}


def test_get_battery_status() -> None:
    """Test battery status command."""
    reset_request_id()
    command = get_battery_status(5)
    parsed = json.loads(command)

    assert parsed["id"] == 1
    assert parsed["method"] == CMD_BATTERY_STATUS
    assert parsed["params"] == {"id": 5}


def test_get_es_status() -> None:
    """Test ES status command."""
    reset_request_id()
    command = get_es_status(0)
    parsed = json.loads(command)

    assert parsed["id"] == 1
    assert parsed["method"] == CMD_ES_STATUS
    assert parsed["params"] == {"id": 0}


def test_get_es_mode() -> None:
    """Test ES mode command."""
    reset_request_id()
    command = get_es_mode(0)
    parsed = json.loads(command)

    assert parsed["id"] == 1
    assert parsed["method"] == CMD_ES_MODE
    assert parsed["params"] == {"id": 0}


def test_get_pv_status() -> None:
    """Test PV status command."""
    reset_request_id()
    command = get_pv_status(0)
    parsed = json.loads(command)

    assert parsed["id"] == 1
    assert parsed["method"] == CMD_PV_GET_STATUS
    assert parsed["params"] == {"id": 0}
