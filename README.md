# goodwe-modbus

Python library to communicate with Goodwe inverters over Modbus.

Built on top of [`modbus-connection`](https://pypi.org/project/modbus-connection/), a framework that maps Modbus register maps to typed Python objects.

## Installation

```bash
pip install goodwe-modbus
```

## Quick start

```python
import asyncio
from modbus_connection import ModbusConnection, ModbusTcpParams
from goodwe_modbus import GoodweInverter

async def main():
    connection = ModbusConnection(
        ModbusTcpParams(host="10.0.0.234", port=502),
    )
    await connection.connect()
    try:
        unit = connection.for_unit(246)
        device = GoodweInverter(unit)
        await device.async_update()

        print(f"Serial: {device.identity.serial}")
        print(f"Model: {device.identity.type}")
        print(f"State: {device.state.system_state}")
        print(f"Grid power: {device.grid.power} W")
        print(f"Temperature: {device.state.inverter_temperature} C")
        print(f"Energy today: {device.energy.daily_energy} kWh")
        print(f"Energy total: {device.energy.lifetime_energy} kWh")
    finally:
        await connection.close()

asyncio.run(main())
```

## API

### GoodweInverter

The top-level object. Reach it through a ModbusUnit:

```python
device = GoodweInverter(unit)
await device.async_update()
```

#### Sub-components

| Attribute    | Type               | Description                    |
|--------------|--------------------|--------------------------------|
| identity     | Identity           | Serial number and model        |
| state        | InverterState      | System state, faults, temperature |
| grid         | GridOutput         | AC voltages, currents, power   |
| pv           | PvStrings          | PV string voltage/current/power |
| energy       | EnergyTotals       | Daily and lifetime energy       |
| powercontrol | ActivePowerControl | Active power limit settings   |

#### Update methods

| Method                     | Polls                    |
|----------------------------|--------------------------|
| async_update()             | All sub-systems          |
| async_update_readings()    | pv, state, grid, energy |
| async_update_settings()    | powercontrol             |

### Writing settings

```python
await device.powercontrol.async_set_active_power_export_limit(75)
```

Limits export to 75 % of rated output.

### CLI tool

A command-line query tool is included:

```bash
# TCP connection
python -m goodwe_modbus.query --host 10.0.0.234 --port 502 --unit 246

# Serial over TCP (socket://)
python -m goodwe_modbus.query --device socket://10.0.0.234:502 --unit 246
```

## Development

```bash
git clone https://github.com/theneweinstein/goodwe_modbus.git
cd goodwe_modbus
uv sync
```

### Linting

```bash
ruff check .
ruff format --check .
```

## Related

- [ha-goodwe-modbus](https://github.com/theneweinstein/ha-goodwe-modbus) -- Home Assistant integration that uses this library.
