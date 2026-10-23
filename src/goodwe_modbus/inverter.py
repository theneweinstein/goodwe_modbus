"""Inverter state, identity and on-grid output."""

from __future__ import annotations

from modbus_connection.model import Component, enum, flags, gauge, integer, string, uint32

from .enums import (
    Fault1,
    SystemState,
)
from .faults import FAULTS_BY_ID, Fault


class InverterState(Component):
    """Inverter state, identity and on-grid output."""

    max_span = 2

    system_state = enum(564, SystemState, signed=False)
    fault = flags(544, Fault1, count=2, signed=False)
    generation_time_total = uint32(548, unit="h")
    inverter_temperature = gauge(565, 0.1, signed=False, unit="°C")

    @property
    def active_faults(self) -> frozenset[Fault]:
        """Every fault the inverter currently reports.

        ``Fault1`` is an ``IntFlag`` whose individual members correspond to
        bit positions; the fault ID is the 1-based bit index.

        >>> Fault1.ID001_GFCI_CHECK  # bit 0 -> fault id 1
        <Fault1.ID001_GFCI_CHECK: 1>
        >>> Fault1.ID007_GFCI        # bit 6 -> fault id 7
        <Fault1.ID007_GFCI: 64>
        """
        return frozenset(
            fault
            for member in self.fault
            if (fault := FAULTS_BY_ID.get(member.value.bit_length())) is not None
        )

class Identity(Component):
    """Inverter identity."""

    type = string(528, 5)
    """Inverter type"""
    serial = string(512, 8)
    """Inverter serial number."""

class GridOutput(Component):
    """Inverter grid output."""

    max_span = 2

    voltage_l1 = gauge(554, 0.1, unit="V")
    voltage_l2 = gauge(555, 0.1, unit="V")
    voltage_l3 = gauge(556, 0.1, unit="V")
    current_l1 = gauge(557, 0.1, unit="A")
    current_l2 = gauge(558, 0.1, unit="A")
    current_l3 = gauge(559, 0.1, unit="A")
    frequency_l1 = gauge(560, 0.01, unit="Hz")
    frequency_l2 = gauge(561, 0.01, unit="Hz")
    frequency_l3 = gauge(562, 0.01, unit="Hz")
    power = integer(563, unit="W")

    @property
    def power_l1(self) -> float:
        """Grid output power on L1 in W."""
        return self.voltage_l1 * self.current_l1

    @property
    def power_l2(self) -> float:
        """Grid output power on L2 in W."""
        return self.voltage_l2 * self.current_l2

    @property
    def power_l3(self) -> float:
        """Grid output power on L3 in W."""
        return self.voltage_l3 * self.current_l3

