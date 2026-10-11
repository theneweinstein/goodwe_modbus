"""Settings and commands."""

from __future__ import annotations

from modbus_connection.model import Component, integer

class ActivePowerControl(Component):
    """Active power control settings."""

    active_power_export_limit = integer(256, signed = False, unit = "%")
    """Active power export limit in W."""

    async def async_set_active_power_export_limit(self, limit: float) -> None:
        """Set the active power export limit in W."""
        if not 0 <= limit <= 100:
            raise ValueError(f"active power limit {limit}% is outside 0-100")
        await self._unit.write_register(256, round(limit))