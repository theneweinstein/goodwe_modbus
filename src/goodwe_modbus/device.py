"""The top-level object for a current-generation Goodwe inverter."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from modbus_connection.model import (
    Device,
    Raw,
    UpdateReport,
)

from .energy import EnergyTotals
from .inverter import InverterState, Identity, GridOutput
from .pv import PvStrings
from .settings import ActivePowerControl


if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

# Attribute names of the sub-systems each update method reads.
READINGS = ("pv", "state", "grid", "energy")
SETTINGS = ("powercontrol",)
ALL = ("identity", *READINGS, *SETTINGS)

class GoodweInverter(Device):
    """A current-generation Goodwe inverter reached through a ``ModbusUnit``."""


    def __init__(
        self,
        unit: ModbusUnit,
    ) -> None:
        """Set up the sub-systems."""
        super().__init__(unit)

        self.energy = EnergyTotals(unit)
        self.grid = GridOutput(unit)
        self.identity = Identity(unit)
        self.state = InverterState(unit)
        self.pv = PvStrings(unit)
        self.powercontrol = ActivePowerControl(unit)

    async def _async_setup(self) -> None:
        """Read the identity once; serial number and model never change."""
        try:
            await self.identity.async_update()
        except Exception:
            # If the inverter is offline we still mark setup as done so
            # that subsequent polls do not re-attempt the identity read
            # (and time out again).  The identity will be read on the
            # first successful poll after the inverter comes back online.
            self._setup_done = True
            raise

    async def async_update_readings(self) -> UpdateReport:
        """Update the readings sub-systems."""
        return await self.async_poll(READINGS)

    async def async_update_settings(self) -> UpdateReport:
        """Refresh what the controller has been configured to do."""
        return await self.async_poll(SETTINGS)

    async def async_update(self) -> UpdateReport:
        """Refresh all components (readings and settings)."""
        report = await self.async_poll(READINGS)
        return await self.async_poll(SETTINGS, report)

    async def async_update_grid(self) -> UpdateReport:
        """Refresh only the grid output component."""
        return await self.async_poll(("grid",))

    async def async_read_raw(self, names: Iterable[str] = ALL) -> Raw:
        """Every register this device reads, undecoded, for diagnostics."""
        return await super().async_read_raw(names)

