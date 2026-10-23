"""Tests for the goodwe-modbus library."""

from __future__ import annotations

from modbus_connection.mock import MockModbusConnection
from modbus_connection.pytest_plugin import mock_modbus_connection, mock_modbus_unit  # noqa: F401

from goodwe_modbus import GoodweInverter
from goodwe_modbus.enums import SystemState


def _encode_string(text: str, count: int) -> list[int]:
    """Encode a string into register values (2 chars per register, big-endian)."""
    registers = []
    for i in range(count):
        offset = i * 2
        high = ord(text[offset]) if offset < len(text) else 0
        low = ord(text[offset + 1]) if offset + 1 < len(text) else 0
        registers.append(high << 8 | low)
    return registers


def _set_holding(unit, address: int, values: list[int]) -> None:
    """Set holding register values starting at *address*."""
    for offset, value in enumerate(values):
        unit.holding[address + offset] = value


async def _device() -> tuple[MockModbusConnection, GoodweInverter]:
    """Create a fresh device with an in-memory Modbus connection.

    Returns (connection, device) so callers can configure registers
    and then update.
    """
    conn = MockModbusConnection()
    unit = conn.for_unit(246)

    # Populate identity registers (serial at 512-519, type at 528-532).
    _set_holding(unit, 512, _encode_string("SN1234567890", 8))
    _set_holding(unit, 528, _encode_string("GW10K-ET", 5))

    # Populate state registers.
    _set_holding(unit, 544, [0x0000, 0x0000])  # fault = 0 (no faults)
    _set_holding(unit, 548, [0x0000, 0x0001])  # generation_time_total = 1
    _set_holding(unit, 564, [1])                # system_state = NORMAL
    _set_holding(unit, 565, [230])              # inverter_temperature = 23.0 C

    # Populate grid output registers.
    _set_holding(unit, 554, [2300])  # voltage_l1 = 230.0 V
    _set_holding(unit, 555, [2310])  # voltage_l2 = 231.0 V
    _set_holding(unit, 556, [2290])  # voltage_l3 = 229.0 V
    _set_holding(unit, 557, [50])    # current_l1 = 5.0 A
    _set_holding(unit, 558, [45])    # current_l2 = 4.5 A
    _set_holding(unit, 559, [48])    # current_l3 = 4.8 A
    _set_holding(unit, 560, [5001])  # frequency_l1 = 50.01 Hz
    _set_holding(unit, 561, [5000])  # frequency_l2 = 50.00 Hz
    _set_holding(unit, 562, [4999])  # frequency_l3 = 49.99 Hz
    _set_holding(unit, 563, [1500])  # power = 1500 W

    # Populate PV registers (repeating group count=2, stride=1).
    # Instance 0: pv_voltage@550, pv_current@552
    # Instance 1: pv_voltage@551, pv_current@553
    _set_holding(unit, 550, [3600])  # string 1: voltage=360.0V
    _set_holding(unit, 552, [35])    # string 1: current=3.5A
    _set_holding(unit, 551, [3400])  # string 2: voltage=340.0V
    _set_holding(unit, 553, [30])    # string 2: current=3.0A

    # Populate energy registers.
    _set_holding(unit, 546, [0x0000, 0x03E8])  # lifetime_energy = 1000 -> 100.0 kWh
    _set_holding(unit, 566, [50])               # daily_energy = 50 (gauge 0.1) = 5.0 kWh

    # Populate power control register.
    _set_holding(unit, 256, [75])  # active_power_export_limit = 75%

    device = GoodweInverter(unit)
    await device.async_ensure_setup()
    return conn, device


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


async def test_identity() -> None:
    _, device = await _device()

    assert device.identity.serial == "SN1234567890"
    assert device.identity.type == "GW10K-ET"


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


async def test_state_normal() -> None:
    _, device = await _device()
    await device.async_update_readings()

    assert device.state.system_state == SystemState.NORMAL
    assert device.state.generation_time_total == 1
    assert device.state.inverter_temperature == 23.0
    assert device.state.active_faults == frozenset()


async def test_state_with_faults() -> None:
    conn, device = await _device()
    # Set fault bits: ID001 (0x01) and ID007 (0x40) -> 0x0041
    # flags(544, Fault1, count=2) reads big-endian: value = (reg544 << 16) | reg545
    _set_holding(conn.for_unit(246), 544, [0x0000, 0x0041])
    await device.async_update_readings()

    faults = {f.id for f in device.state.active_faults}
    assert 1 in faults  # ID001_GFCI_CHECK
    assert 7 in faults  # ID007_GFCI
    assert len(faults) == 2


# ---------------------------------------------------------------------------
# Grid output
# ---------------------------------------------------------------------------


async def test_grid_output() -> None:
    _, device = await _device()
    await device.async_update_readings()

    assert device.grid.voltage_l1 == 230.0
    assert device.grid.voltage_l2 == 231.0
    assert device.grid.voltage_l3 == 229.0
    assert device.grid.current_l1 == 5.0
    assert device.grid.current_l2 == 4.5
    assert device.grid.current_l3 == 4.8
    assert device.grid.frequency_l1 == 50.01
    assert device.grid.frequency_l2 == 50.00
    assert device.grid.frequency_l3 == 49.99
    assert device.grid.power == 1500

    assert device.grid.power_l1 == 230.0 * 5.0  # 1150.0
    assert device.grid.power_l2 == 231.0 * 4.5  # 1039.5
    assert device.grid.power_l3 == 229.0 * 4.8  # 1099.2


# ---------------------------------------------------------------------------
# PV strings
# ---------------------------------------------------------------------------


async def test_pv_strings() -> None:
    _, device = await _device()
    await device.async_update_readings()

    strings = device.pv.strings
    assert len(strings) == 2

    assert strings[0].pv_voltage == 360.0
    assert strings[0].pv_current == 3.5
    assert strings[0].pv_power == 360.0 * 3.5  # 1260.0

    assert strings[1].pv_voltage == 340.0
    assert strings[1].pv_current == 3.0
    assert strings[1].pv_power == 340.0 * 3.0  # 1020.0


# ---------------------------------------------------------------------------
# Energy
# ---------------------------------------------------------------------------


async def test_energy() -> None:
    _, device = await _device()
    await device.async_update_readings()

    assert device.energy.daily_energy == 5.0
    assert device.energy.lifetime_energy == 100.0


# ---------------------------------------------------------------------------
# Power control
# ---------------------------------------------------------------------------


async def test_power_control_read() -> None:
    _, device = await _device()
    await device.async_update_settings()

    assert device.powercontrol.active_power_export_limit == 75


async def test_power_control_write() -> None:
    conn, device = await _device()
    await device.async_update_settings()
    assert device.powercontrol.active_power_export_limit == 75

    # Write a new limit.
    await device.powercontrol.async_set_active_power_export_limit(50)
    assert conn.for_unit(246).holding[256] == 50

    # Re-read and verify.
    await device.async_update_settings()
    assert device.powercontrol.active_power_export_limit == 50


async def test_power_control_write_out_of_range() -> None:
    _, device = await _device()
    try:
        await device.powercontrol.async_set_active_power_export_limit(150)
        assert False, "expected ValueError"
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# Full update
# ---------------------------------------------------------------------------


async def test_async_update() -> None:
    _, device = await _device()
    report = await device.async_update()

    assert "pv" in report.updated
    assert "state" in report.updated
    assert "grid" in report.updated
    assert "energy" in report.updated
    assert "powercontrol" in report.updated
    assert not report.failed


async def test_async_update_grid() -> None:
    _, device = await _device()
    report = await device.async_update_grid()

    assert "grid" in report.updated
    assert len(report.updated) == 1
    assert not report.failed


# ---------------------------------------------------------------------------
# async_read_raw
# ---------------------------------------------------------------------------


async def test_async_read_raw() -> None:
    _, device = await _device()
    raw = await device.async_read_raw(("identity",))

    assert "holding" in raw
    registers = raw["holding"]
    assert registers[512] == ord("S") << 8 | ord("N")  # "SN"
    assert registers[513] == ord("1") << 8 | ord("2")  # "12"
