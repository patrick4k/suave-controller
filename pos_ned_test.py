#!/usr/bin/env python3

"""
Caveat when attempting to run the examples in non-gps environments:

`drone.offboard.stop()` will return a `COMMAND_DENIED` result because it
requires a mode switch to HOLD, something that is currently not supported in a
non-gps environment.
"""

import asyncio

from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw, Attitude)


async def run():
    """ Does Offboard control using position NED coordinates. """

    drone = System()
    connection_string = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_B0019BWS-if00-port0"
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

    print("-- Arming")
    await drone.action.arm()
    print("-- Drone is Armed")

    print("-- Setting Attitude Setpoint")
    await drone.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.0))

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed \
                with error code: {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return

    print("-- Setting initial setpoint")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    
    async def goto(n, e, d):
        print(f"-- Go {n}m North, {e}m East, {d}m Down")
        await drone.offboard.set_position_ned(PositionNedYaw(n, e, d, 0))
        await asyncio.sleep(10)

    # FLIGHT PLAN
    asyncio.sleep(5)
    print("-- Starting Flight plan")
    await goto(0,0,-1)
    await goto(0,0,1)

    print("-- Disarming drone")
    await drone.action.disarm()

    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed \
                with error code: {error._result.result}")


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())