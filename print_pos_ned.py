#!/usr/bin/env python3

"""
Caveat when attempting to run the examples in non-gps environments:

`drone.offboard.stop()` will return a `COMMAND_DENIED` result because it
requires a mode switch to HOLD, something that is currently not supported in a
non-gps environment.
"""

import asyncio

from mavsdk import System
from mavsdk.telemetry import (PositionVelocityNed, PositionNed)
from mavsdk.offboard import PositionNedYaw


async def run():
    """ Does Offboard control using position NED coordinates. """

    drone = System()
    connection_string = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A10L1BX5-if00-port0"
    address = f"serial://{connection_string}:57600"
    await drone.connect(system_address=address)

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    # print("Waiting for drone to have a global position estimate...")
    # async for health in drone.telemetry.health():
    #     if health.is_global_position_ok and health.is_home_position_ok:
    #         print("-- Global position estimate OK")
    #         break
        
    async def getpos():
        async for posvelned in drone.telemetry.position_velocity_ned():
            return posvelned.position
        print("-- ERROR: Could not find pos in telemetry")

    async def printned():
        posned = await getpos()
        print(f"-- POS: {posned.north_m}m North, {posned.east_m}m East, {posned.down_m}m Down")

    while True:
        await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
        await printned()
        await asyncio.sleep(1)

if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
