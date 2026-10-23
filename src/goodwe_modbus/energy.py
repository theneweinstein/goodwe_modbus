"""Daily and lifetime energy counters"""

from __future__ import annotations

from modbus_connection.model import Component, uint32, gauge

class EnergyTotals(Component):
    """Daily and lifetime energy counters"""

    max_span = 2

    daily_energy = gauge(566, 0.1, signed=False, unit="kWh")
    """Daily energy in kWh."""

    lifetime_energy = uint32(546, scale = 0.1, unit="kWh")
    """Lifetime energy in kWh."""