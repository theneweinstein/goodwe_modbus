import argparse
import asyncio

from modbus_connection import ModbusError
from modbus_connection.cli_helper import (
    CountingUnit,
    add_connection_args,
    connect_from_args,
    print_component,
)

from goodwe_modbus import GoodweInverter, ALL

async def main() -> int:
    parser = argparse.ArgumentParser(description="Query a device and print values.")
    add_connection_args(parser)
    # The unit id is not part of connecting. It varies per device and per tool,
    # so add whatever the CLI needs alongside the connection arguments.
    parser.add_argument("--unit", type=int, default=1, help="Modbus unit id")
    args = parser.parse_args()

    try:
        conn = await connect_from_args(args)
    except ModbusError as err:
        print(f"Could not connect: {err}")
        return 1

    counting = CountingUnit(conn.for_unit(args.unit))
    try:
        device = GoodweInverter(counting)
        await device.async_update()
    finally:
        await conn.close()

    for member in ALL:
        print_component(getattr(device, member))
    print(f"\n{counting.reads} Modbus reads")
    return 0


raise SystemExit(asyncio.run(main()))