"""The top-level object for a current-generation Sofar inverter."""

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
READINGS = ("pv","state","grid","energy")
SETTINGS = ("powercontrol",)
ALL = ("identity", *READINGS, *SETTINGS)

class GoodweInverter(Device):
    """A current-generation Goodwe inverter reached through a ``ModbusUnit``."""


    def __init__(
        self,
        unit: ModbusUnit,
    ) -> None:
        """Set up the sub-systems.

        ``read_pm`` reads parallel-system registers an inverter refuses.
        """
        super().__init__(unit)

        self.energy = EnergyTotals(unit)
        self.grid = GridOutput(unit)
        self.identity = Identity(unit)
        self.state = InverterState(unit)
        self.pv = PvStrings(unit)
        self.powercontrol = ActivePowerControl(unit)

    async def _async_setup(self) -> None:
        """Set up the sub-systems."""
        await self.identity.async_update()

    async def async_update_readings(self) -> UpdateReport:
        """Update the readings sub-systems."""
        return await self.async_poll(READINGS)

    async def async_update_settings(self) -> UpdateReport:
        """Refresh what the controller has been configured to do."""
        return await self.async_poll(SETTINGS)

    async def async_update(self) -> UpdateReport:
        """Refresh all components."""
        report = await self.async_poll(READINGS)
        return await self.async_poll(SETTINGS, report)

    async def async_read_raw(self, names: Iterable[str] = ALL) -> Raw:
        """Every register this device reads, undecoded, for diagnostics."""
        return await super().async_read_raw(names)




