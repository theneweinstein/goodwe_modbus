"""PV strings, one component per MPPT tier."""

from __future__ import annotations

from modbus_connection.model import Component, gauge, repeating_group



class PvString(Component):
    """A PV string, one component per MPPT tier."""

    pv_voltage = gauge(550,0.1, stride = 1, unit="V")
    """PV voltage in V."""
    pv_current = gauge(552,0.1, stride = 1, unit="A")
    """PV current in A."""

    @property
    def pv_power(self) -> float:
        """PV power in W."""
        return self.pv_voltage * self.pv_current

class PvStrings(Component):
    """A PV string, one component per MPPT tier."""

    strings = repeating_group(2, PvString, stride = 1)