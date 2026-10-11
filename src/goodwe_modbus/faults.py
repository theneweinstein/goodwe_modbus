"""Fault definitions, keyed by vendor ID rather than register."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

class FaultCategory(StrEnum):
    """The subsystem a fault belongs to."""

    AC_OUTPUT = "ac_output"
    COMMUNICATION = "communication"
    DC_BUS = "dc_bus"
    FAN = "fan"
    GRID = "grid"
    INSULATION = "insulation"
    INTERNAL = "internal"
    PV = "pv"
    SALES = "sales"
    THERMAL = "thermal"

@dataclass(frozen=True, slots=True)
class Fault:
    """One fault the inverter can report."""

    id: int
    key: str
    category: FaultCategory

FAULTS: tuple[Fault, ...] = (
    Fault(1, "gfci_check_fail", FaultCategory.INTERNAL),
    Fault(2, "ac_hct_check_fail", FaultCategory.INTERNAL),
    Fault(3, "ref_v", FaultCategory.INTERNAL),
    Fault(4, "dc_switch_fault", FaultCategory.DC_BUS),
    Fault(5, "dc_spd_fault", FaultCategory.DC_BUS),
    Fault(6, "sales1", FaultCategory.SALES),
    Fault(7, "gfci_fault", FaultCategory.INTERNAL),
    Fault(8, "relay_fault", FaultCategory.INTERNAL),
    Fault(9, "ac_hct", FaultCategory.INTERNAL),
    Fault(10, "utility_loss", FaultCategory.GRID),
    Fault(11, "ground_fault", FaultCategory.INSULATION),
    Fault(12, "dc_bus_high", FaultCategory.DC_BUS),
    Fault(13, "internal_fan_fault", FaultCategory.FAN),
    Fault(14, "over_temperature", FaultCategory.THERMAL),
    Fault(15, "sales2", FaultCategory.SALES),
    Fault(16, "pv_overvoltage", FaultCategory.PV),
    Fault(17, "external_fan_fault", FaultCategory.FAN),
    Fault(18, "vac_fault", FaultCategory.GRID),
    Fault(19, "isolation_fault", FaultCategory.INSULATION),
    Fault(20, "high_dc_component", FaultCategory.GRID),
    Fault(21, "lcd_communication_fault", FaultCategory.COMMUNICATION),
    Fault(22, "string_over_current", FaultCategory.PV),
    Fault(23, "pv_reverse_fault", FaultCategory.PV),
    Fault(24, "export_power_limit_fault", FaultCategory.GRID),
    Fault(25, "npe", FaultCategory.GRID),
    Fault(26, "relay_check_fault", FaultCategory.INTERNAL),
    Fault(27, "lpe", FaultCategory.GRID),
    Fault(28, "night_sps_fault", FaultCategory.INTERNAL),
    Fault(29, "afci_fault", FaultCategory.INTERNAL),
    Fault(30, "grid_frequency_overrun", FaultCategory.GRID),
    Fault(31, "eeprom", FaultCategory.COMMUNICATION),
    Fault(32, "spi_fault", FaultCategory.COMMUNICATION)
)


FAULTS_BY_ID: dict[int, Fault] = {fault.id: fault for fault in FAULTS}