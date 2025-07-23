"""
This file is part of ts_ATHexapod

Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
This product includes software developed by the LSST Project
(https://www.lsst.org).
See the COPYRIGHT file at the top-level directory of this distribution
For details of code ownership.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABLITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have recieved a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import logging

from lsst.ts import tcpip


class ATHexapodController:
    """Implements wrapper around ATHexapod server.

    Attributes
    ----------
    host : `str`
        The address of the host.
    port : `int`
        The port to connect to.
    timeout : `float`
        The regular timeout.
    long_timeout : `float`
        The longer timeout for actions which move the hexapod.
    reader : `asyncio.StreamReader`
        The asynchronous reader.
    writer : `asyncio.StreamWriter`
        The asynchronous writer.
    lock : `asyncio.Lock`
        The lock on the connection.
    log : `logging.Logger`
        The log for this class.

    Parameters
    ----------
    log : `logging.Logger` or `None`
        Provide preconfigured log or None to create a default one.

    """

    def __init__(
        self,
        log: None | logging.Logger = None,
        host: str = tcpip.LOCAL_HOST,
        port: int = 50000,
        timeout: float = 2.0,
    ) -> None:
        self.host: str = host
        self.port: int = port
        self.timeout: float = timeout

        self.reader: None = None
        self.writer: None = None

        self.lock: asyncio.Lock = asyncio.Lock()

        if log is None:
            self.log: logging.Logger = logging.getLogger(__name__)
        else:
            self.log = log
        self.client: tcpip.Client = tcpip.Client(host="", port=None, log=self.log)
        self.log.debug("Controller created")

    @property
    def is_connected(self) -> bool:
        """Check if connected to the controller.

        Returns
        -------
        connected : `bool`

        """
        return self.client.connected

    async def connect(self) -> None:
        """Connect to hexapod controller."""
        self.client = tcpip.Client(
            host=self.host, port=self.port, log=self.log, encoding="ISO-8859-1", terminator=b"\n"
        )
        await self.client.start_task

    async def disconnect(self) -> None:
        """Disconnect from hexapod controller."""

        await self.client.close()
        await self.client.done_task
        self.client = tcpip.Client(host="", port=None, log=self.log)

    async def write_command(self, cmd: str, has_response: bool = True, num_line: int = 1) -> None | list[str]:
        """Send command to hexapod controller and return response.

        Parameters
        ----------
        cmd : `str`
            Command to send to hexapod. A 'newline' character will be appended.
        has_response : `bool`
            Does the command have a response?
        num_line : `int`
            The number of expected lines/replies.

        Returns
        -------
        replies : `list`
            List with the response(s) from the command.

        """

        async with self.lock:
            if not self.client.connected:
                raise RuntimeError("Not connected to hexapod controller. Call `connect` first")

            await self.client.write_str(cmd)

            if has_response:
                try:
                    replies: list[str] = []
                    for i in range(num_line):
                        line = await self.client.readline()
                        line = line.strip(self.client.terminator).decode(self.client.encoding)
                        self.log.debug(f"Read {i + 1} of {num_line} lines: {line}")
                        replies.append(line)
                except TimeoutError:
                    self.log.warning(
                        "Timed out waiting for response from controller. Result may be incomplete."
                    )
                    raise

                return replies
            else:
                return None

    async def real_position(self) -> list[float]:
        """Return parsed real position string

        (p. 138) Get Real Position. This command is identical in function to
        POS? (p. 216), but only one character has to be sent via the
        interface. Therefore #3 can also be used while the controller is
        performing timeconsuming tasks. Between the switching-on of the
        controller and the reference point definition of the Hexapod with FRF
        (p. 174), the current position of the Hexapod and axes A and B is
        unknown. Nevertheless, the response to #3 gives the position value 0
        for all axes.

        Returns
        -------
        real_pos : `tuple` of (`float`, `float`, `float`, `float`, `float`,
                    `float`)
            Positions for the X (mm), Y (mm), Z (mm), U (deg), V (deg),
            W (deg) axis.

        """
        ret = await self.write_command("\3", num_line=6)
        assert ret is not None

        return [float(val.split("=")[1]) for val in ret]

    async def motion_status(self) -> tuple[bool, ...]:
        """Return parsed motion status string.

        (p. 140) Request Motion Status. Axes 1 to 8 correspond to the X, Y, Z,
        U, V, W, A and B axes in this order. Exception: When the "NOSTAGE"
        stage type is assigned to an axis (possible for axes A and B; query
        with the CST? (p. 152) command), this axis is not included in the
        bitmapped answer. In this case, it is skipped when counting the
        axes.

        Returns
        -------
        is_moving : `tuple` of (`bool`, `bool`, `bool`, `bool`, `bool`, `bool`)

        """
        ret = await self.write_command("\5", num_line=1)
        assert ret is not None

        code = int(ret[0], 16)

        return tuple([(code & (1 << i)) > 0 for i in range(6)])

    async def position_changed(self) -> tuple[bool, ...]:
        """Return parsed position changed response.

        Queries whether the axis positions have changed since the last
        position query was sent.
        Response:
        The response <uint> is a bit mask and returned as the hexadecimal
        sum of the following codes:

        1 = Position of the first axis has changed
        2 = Position of the second axis has changed
        4 = Posiiton of the third axis has changed
        ...

        Reads response from server and returns a parsed response.

        Returns
        -------
        pos_changed : `tuple` of (`bool`, `bool`, `bool`, `bool`, `bool`,
                      `bool`)
            The value of each axis changed or not.

        """
        ret = await self.write_command("\6", num_line=1)
        assert ret is not None

        code = int(ret[0])

        return tuple([(code & (1 << i)) > 0 for i in range(6)])

    async def controller_ready(self) -> bool:
        """Return parsed controller ready response.

        (p. 141) Request Controller Ready Status Asks controller for ready
        status (tests if controller is ready to perform a new command)

        B1h (ASCII character 177) if controller is ready B0h (ASCII character
        176) if controller is not ready (e.g., performing a reference move)

        Returns
        -------
        comp : `str`
            A character indicating the controller is ready or not ready.
        """
        ret = await self.write_command("\7", num_line=1)
        assert ret is not None

        comp = ret == chr(177)
        self.log.debug(f"ret={ret} : {chr(177)} : comp={comp}")

        return comp

    async def stop_all_axes(self) -> None:
        """Stop all axes.

        (p. 143) Stop All Axes To confirm that this worked, #5 has to be used.
        """
        await self.write_command(chr(24), has_response=False)

    async def set_position(
        self,
        x: None | float = None,
        y: None | float = None,
        z: None | float = None,
        u: None | float = None,
        v: None | float = None,
        w: None | float = None,
    ) -> None:
        """Set position of Hexapod.

        (p. 206) Set Target Position

        :Execute:
        :Send: MOV X 10 U 5
        :Note: Axis X moves to 10 (target
        position in mm), axis U moves to
        5 (target position in deg)

        Parameters
        ----------
        x : `None` or `float`
            X-axis position (in mm).
        y : `None` or `float`
            Y-axis position (in mm).
        z : `None` or `float`
            Z-axis position (in mm).
        u : `None` or `float`
            U-axis rotation (in deg).
        v : `None` or `float`
            V-axis rotation (in deg).
        w : `None` or `float`
            W-axis rotation (in deg).
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        await self.write_command("MOV" + target, has_response=False)

    async def referencing_result(self) -> list[float]:
        """Return parsed referencing result response.

        (p. 175) Get Referencing Result
        Axes X, Y, Z, U, V, W, A and B are considered to be
        "referenced" when a reference move has been successfully
        completed with FRF (p. 174).
        Axes A and B are considered to be "referenced" even if the
        parameter Sensor Reference Mode (ID 0x02000A00) was
        changed to value 1 (p. 98) with SPA (p. 224). It is
        necessary to change the parameter value when the
        connected stage is not equipped with a reference point
        switch and can therefore not carry out a reference move.
        Axes K, L and M are equipped with absolute-measuring
        sensors and do not need a reference move. For this reason,
        FRF? always responds with 1 for these axes.
        This controller only responds with X Y Z U V W axes.

        Returns
        -------
        response : `list` of `float`
            The current status of axii referenced or not referenced.
        """
        ret = await self.write_command("FRF?", num_line=6)
        assert ret is not None

        return [float(val.split("=")[1]) == 1 for val in ret]

    async def reference(self) -> None:
        """Perform a reference in all axes."""
        await self.write_command("FRF X Y Z U V W", has_response=False)

    async def target_position(self) -> list[float]:
        """Return parsed target position response.

        (p. 208) Get Target Position

        MOV? gets the commanded positions. Use POS? (p. 216) to get the
        current positions.

        Returns
        -------
        response : `list` of `float`
            The current target position.
        """
        ret = await self.write_command("MOV? X Y Z U V W", num_line=6)
        assert ret is not None

        return [float(val.split("=")[1]) for val in ret]

    async def set_low_position_soft_Limit(
        self,
        x: None | float = None,
        y: None | float = None,
        z: None | float = None,
        u: None | float = None,
        v: None | float = None,
        w: None | float = None,
    ) -> None:
        """Set lower position software limit.

        (p. 212) Set Low Position Soft Limit

        Limits the low end of the axis travel range in closed-loop operation
        ("soft limit").

        Parameters
        ----------
        x : `None` or `float`
            The X axis lower limit.
        y : `None` or `float`
            The Y axis lower limit.
        z : `None` or `float`
            The Z axis lower limit.
        u : `None` or `float`
            The U axis lower limit.
        v : `None` or `float`
            The V axis lower limit.
        w : `None` or `float`
            The W axis lower limit.
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        await self.write_command("NLM" + target, has_response=False)

    async def get_low_position_soft_limit(self) -> list[float]:
        """Return parsed lower position software limit response.

        Get the position "soft limit" which determines the low end of
        the axis travel range in closed-loop operation.

        Returns
        -------
        response : `list` of `float`
            The current lower limit values.
        """
        ret = await self.write_command("NLM? X Y Z U V W", num_line=6)
        assert ret is not None

        return [float(val.split("=")[1]) for val in ret]

    async def set_high_position_soft_limit(
        self,
        x: None | float = None,
        y: None | float = None,
        z: None | float = None,
        u: None | float = None,
        v: None | float = None,
        w: None | float = None,
    ) -> None:
        """Set the higher position software limit.

        (p. 214) Set High Position Soft Limit

        Limits the high end of the axis travel range in closed-loop
        operation ("soft limit").

        Parameters
        ----------
        x : `None` or `float`
            The X axis higher limit.
        y : `None` or `float`
            The Y axis higher limit.
        z : `None` or `float`
            The Z axis higher limit.
        u : `None` or `float`
            The U axis higher limit.
        v : `None` or `float`
            The V axis higher limit.
        w : `None` or `float`
            The W axis higher limit.
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        await self.write_command("PLM" + target, has_response=False)

    async def get_high_position_soft_limit(self) -> list[float]:
        """Return parsed higher position software limit response.

        Returns
        -------
        response : `list` of `float`
            The current higher limit values.
        """
        ret = await self.write_command("PLM? X Y Z U V W", num_line=6)
        assert ret is not None

        return [float(val.split("=")[1]) for val in ret]

    async def on_target(self) -> list[float]:
        """Return parsed on target response

        (p. 213) Get On Target State

        Gets on-target state of given axis.

        if all arguments are omitted, gets state of all axes.

        Returns
        -------
        response : `list` of `float`
            Current on target status of all axii.
        """
        ret = await self.write_command("ONT?", num_line=6)
        assert ret is not None

        return [float(val.split("=")[1]) == 1 for val in ret]

    async def get_position_unit(self) -> list[str]:
        """Return parsed position unit response.

        (p. 217) Get Position Unit

        Get the current unit of the position.

        Returns
        -------
        response : `list` of `str`
            The current units of the axii.
        """
        ret = await self.write_command("PUN? X Y Z U V W", num_line=6)
        assert ret is not None

        return [val.split("=")[1] for val in ret]

    async def offset(
        self,
        x: None | float = None,
        y: None | float = None,
        z: None | float = None,
        u: None | float = None,
        v: None | float = None,
        w: None | float = None,
    ) -> None:
        """Set the offset of the Hexapod.

        (p. 215) Set Target Relative To Current Position
        Moves given axes relative to the last commanded target position.

        Parameters
        ----------
        x : `None` or `float`
            The position to move X axis to.
        y : `None` or `float`
            The position to move Y axis to.
        z : `None` or `float`
            The position to move Z axis to.
        u : `None` or `float`
            The position to move U axis to.
        v : `None` or `float`
            The position to move V axis to.
        w : `None` or `float`
            The position to move W axis to.
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        await self.write_command("MVR" + target, has_response=False)

    async def check_offset(
        self,
        x: None | float = None,
        y: None | float = None,
        z: None | float = None,
        u: None | float = None,
        v: None | float = None,
        w: None | float = None,
    ) -> list[float]:
        """Return parsed check offset response.

        (p. 253) VMO? (Virtual Move)

        Checks whether the moving platform of the Hexapod can approach
        a specified position from the current position.

        Used to validate if MVR command is possible.

        Parameters
        ----------
        x : `None` or `float`
            The position to check.
        y : `None` or `float`
            The position to check.
        z : `None` or `float`
            The position to check.
        u : `None` or `float`
            The position to check.
        v : `None` or `float`
            The position to check.
        w : `None` or `float`
            The position to check.

        Returns
        -------
        response : `list` of `float`
            Whether each axis can make the move.
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        ret = await self.write_command("VMO?" + target, num_line=6)
        assert ret is not None

        return [float(val.split("=")[1]) == 1 for val in ret]

    async def set_pivot_point(
        self, x: None | float = None, y: None | float = None, z: None | float = None
    ) -> None:
        """Set the pivot point of the Hexapod.

        (p. 227)(Set Pivot Point)

        Sets the pivot point coordinates in the volatile memory.
        Can only be set when the following holds true for the rotation
        coordinates of the moving platform: U = V = W = 0

        Returns
        -------
        x : `None` or `float`
            The pivot point of the X axis.
        y : `None` or `float`
            The pivot point of the Y axis.
        z : `None` or `float`
            The pivot point of the Z axis.
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""

        await self.write_command("SPI" + target, has_response=False)

    async def getPivotPoint(self) -> list[float]:
        """Return parsed pivot point response.

        (p. 229) (Get Pivot Point)

        Gets the pivot point coordinates.

        Returns
        -------
        response : `list` of `float`
            The current pivot points of the Hexapod.
        """
        ret = await self.write_command("SPI?", num_line=3)
        assert ret is not None

        return [float(val.split("=")[1]) for val in ret]

    async def check_active_soft_limit(self) -> list[float]:
        """Return parsed response for checking if software limit is active.

        SSL? (p. 230) Get Soft Limit Status

        Returns
        -------
        response : `list` of `float`
            The current status of the software limits for each axis.
        """
        ret = await self.write_command("SSL?", num_line=6)
        assert ret is not None

        return [float(val.split("=")[1]) == 1 for val in ret]

    async def activate_soft_limit(
        self, x: bool = True, y: bool = True, z: bool = True, u: bool = True, v: bool = True, w: bool = True
    ) -> None:
        """Set the software limits as active or not.

        (p. 229) Set Soft Limit

        Activates or deactivates the soft limits that are set with NLM
        (p. 212) and PLM (p. 214).

        Soft limits can only be activated/deactivated when the axis is not
        moving (query with #5 (p. 140)).

        Parameters
        ----------
        x : `bool`
            activate software limit for X axis.
        y : `bool`
            activate software limit for Y axis.
        z : `bool`
            activate software limit for Z axis.
        u : `bool`
            activate software limit for U axis.
        v : `bool`
            activate software limit for V axis.
        w : `bool`
            activate software limit for W axis.
        """
        target = ""
        target += " X " + ("1" if x else "0")
        target += " Y " + ("1" if y else "0")
        target += " Z " + ("1" if z else "0")
        target += " U " + ("1" if u else "0")
        target += " V " + ("1" if v else "0")
        target += " W " + ("1" if w else "0")

        await self.write_command("SSL" + target, has_response=False)

    async def set_clv(
        self,
        x: None | float = None,
        y: None | float = None,
        z: None | float = None,
        u: None | float = None,
        v: None | float = None,
        w: None | float = None,
    ) -> None:
        """Set the closed loop velocity.

        (p. 243) (Set Closed-Loop Velocity)

        The velocity can be changed with VEL while the axis is moving.

        Parameters
        ----------
        x : `None` or `float`
            The velocity of the X axis.
        y : `None` or `float`
            The velocity of the y axis.
        z : `None` or `float`
            The velocity of the z axis.
        u : `None` or `float`
            The velocity of the U axis.
        v : `None` or `float`
            The velocity of the V axis.
        w : `None` or `float`
            The velocity of the W axis.
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        await self.write_command("VEL" + target, has_response=False)

    async def get_clv(self) -> list[float]:
        """Return parsed response for closed loop velocity.

        (p. 244) (Get Closed-Loop Velocity)

        If all arguments are omitted, the value of all axes commanded with
        VEL is queried.

        Returns
        -------
        response : `list` of `float`
            The current closed loop velocity for each axis.
        """
        ret = await self.write_command("VEL?", num_line=6)
        assert ret is not None

        return [float(val.split("=")[1]) == 1 for val in ret]

    async def set_sv(self, velocity: float) -> None:
        """Set the system velocity.

        (p. 251) (Set System Velocity)

        Sets the velocity for the moving platform of the Hexapod

        The velocity can only be set with VLS when the Hexapod
        is not moving (axes X, Y, Z, U, V, W; query with #5 (p. 140)).
        For axes A and B, the velocity can be set with VEL (p. 243).

        Parameters
        ----------
        velocity : `float`
            The platform velocity.
        """
        await self.write_command(f"VLS {velocity}", has_response=False)

    async def get_sv(self) -> float:
        """Return parsed response for system velocity.

        (p. 252) Gets the velocity of the moving platform of the Hexapod
        that is set with VLS (p. 245).

        Returns
        -------
        response : `float`
            The current system velocity.
        """
        ret = await self.write_command("VLS?")
        assert ret is not None
        return float(ret[0])

    async def get_error(self) -> int:
        """Return get error response.

        (p. 163) Get Error Number

        Get error code of the last occurred error and reset the error to 0.

        Returns
        -------
        response : `int`
            The latest error code.
        """
        ret = await self.write_command("ERR?", num_line=1)
        assert ret is not None
        return int(ret[0])
