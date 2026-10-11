import asyncio
from modbus_connection import ModbusSerialParams
from modbus_connection.tmodbus import ModbusConnection
from goodwe_modbus import GoodweInverter


async def main() -> None:
    connection = ModbusConnection(
        ModbusSerialParams(device="socket://10.0.0.234:502")
    )
    try:
        unit = connection.for_unit(246)
        device = GoodweInverter(unit)
        await device.async_update()

        print("Serial number:", device.identity.serial)
        print("Type:", device.identity.type)
        print("State:", device.state.system_state)
        print("Energy:", device.energy.daily_energy, device.energy.lifetime_energy)
        print("Temperature:", device.state.inverter_temperature)
        print("Generation time total:", device.state.generation_time_total)
        print("Faults:", device.state.fault)
        print("Faults:", device.state.active_faults)

        await device.powercontrol.async_set_active_power_export_limit(100)
    finally:
        await connection.close()


asyncio.run(main())