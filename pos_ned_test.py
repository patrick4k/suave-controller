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
from mavsdk.telemetry import (PositionVelocityNed, PositionNed)


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
       
    async def getpos():
        async for posvelned in drone.telemetry.position_velocity_ned():
            return posvelned.position
        print("-- ERROR: Could not find pos in telemetry")

    async def goto(n, e, d, y=0, dt=10):
        posned = await getpos()
        # posned = startpos
        print(f"-- Go {n}m North, {e}m East, {d}m Down from {posned.north_m}m North, {posned.east_m}m East, {posned.down_m}m Down")
        print("-- Setting position NED")
        # await drone.offboard.set_position_ned(PositionNedYaw(n, e, d, 0)) # returns once command is received, not once command is executed
        await drone.offboard.set_position_ned(PositionNedYaw(posned.north_m+n, posned.east_m+e, posned.down_m+d, y))
        print("-- Finished setting position NED")
        await asyncio.sleep(dt)

    # FLIGHT PLAN
    await asyncio.sleep(5)
    startpos = await getpos()
    print(f"-- Initial position: {startpos.north_m}m North, {startpos.east_m}m East, {startpos.down_m}m Down")
    print("-- Starting Flight plan")
    curryaw = 328
    await goto(0,0,-1.5, curryaw, 7)
    await goto(0,0,0,curryaw-45, 5)
    await goto(0,0,0,curryaw+45-360, 5)
    await goto(0,0,1.6, curryaw, 7)

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
