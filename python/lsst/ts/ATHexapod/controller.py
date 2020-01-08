import asyncio
import logging


class ATHexapodController:
    def __init__(self, log=None):

        self.host = '127.0.0.1'
        self.port = 50000
        self.timeout = 2.
        self.long_timeout = 30.

        self.reader = None
        self.writer = None

        self.lock = asyncio.Lock()

        self.log = log

        if self.log is None:
            self.log = logging.getLogger(__name__)

    def is_connected(self):
        """ Check if connected to the controller.

        Returns
        -------
        connected : bool

        """
        return self.reader is not None and self.writer is not None

    async def connect(self):
        """ Connect to hexapod controller.
        """

        async with self.lock:
            if self.is_connected():
                raise RuntimeError("Reader or Writer not None. Try disconnecting first.")

            connect_task = asyncio.open_connection(host=self.host,
                                                   port=self.port)

            self.reader, self.writer = await asyncio.wait_for(connect_task,
                                                              timeout=self.long_timeout)

    async def disconnect(self):
        """ Disconnect from hexapod controller.
        """

        async with self.lock:

            self.reader = None

            if self.writer is not None:
                try:
                    self.writer.write_eof()
                    await asyncio.wait_for(self.writer.drain(), timeout=self.timeout)
                finally:
                    self.writer.close()
                    self.writer = None

    async def write_command(self, cmd, has_response=True, multi_line=True):
        """ Send command to hexapod controller and return response.

        Parameters
        ----------
        cmd : str
            Command to send to hexapod. A '\n' character will be appended.
        has_response : bool
            Does the command have a response?
        multi_line : bool
            Is the response received in multiple lines?

        Returns
        -------
        reponse : str
            String with the response from the command.

        """

        async with self.lock:

            if not self.is_connected():
                raise RuntimeError("Not connected to hexapod controller. "
                                   "Call `connect` first")

            self.log.debug(f"Writing: {cmd.encode()!r}")
            self.writer.write(f"{cmd}\n".encode())
            await self.writer.drain()

            response = b""

            if has_response:
                try:
                    keep_going = multi_line
                    while True:
                        c = await asyncio.wait_for(self.reader.read(1), timeout=2.)
                        response += c

                        if c == b'\n' and not keep_going:
                            break
                        elif c == b' ':
                            keep_going = True
                        elif c == b'\n':
                            keep_going = False
                except asyncio.TimeoutError:
                    self.log.warning("Timed out waiting for response from controller. Result "
                                     "may be incomplete.")

        self.log.debug(f"Response: {response!r}")

        return response

    async def real_position(self):
        """ Get real position command string.

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
        real_pos : tuple(float, float, float, float, float, float)
            Positions for the X (mm), Y (mm), Z (mm), U (deg), V (deg),
            W (deg) axis.

        """
        ret = await self.write_command("\3")

        return [float(val.split("=")[1]) for val in ret.decode().replace("\n", "").split(" ")]

    async def motion_status(self):
        """Generate requestMotionStatus command string.

        (p. 140) Request Motion Status. Axes 1 to 8 correspond to the X, Y, Z,
        U, V, W, A and B axes in this order. Exception: When the "NOSTAGE"
        stage type is assigned to an axis (possible for axes A and B; query
        with the CST? (p. 152) command), this axis is not included in the
        bitmapped answer. In this case, it is skipped when counting the
        axes.

        Return
        ------
        is_moving : tuple(bool, bool, bool, bool, bool, bool)

        """
        ret = await self.write_command("\5", multi_line=False)

        code = int(ret.decode())

        return tuple([(code & (1 << i)) > 0 for i in range(6)])

    async def position_changed(self):
        """Generate qieryForPositionChange command string.

        Queries wheter the axis positions have changed since the last position query was sent.
        Response:
        The response <uint> is bit-mappet and returned as the hexadecimal sum of the following codes:
        1 = Position of the first axis has changed
        2 = Position of the second axis has changed
        4 = Posiiton of the third axis has changed
        ...

        Return
        ------
        pos_changed : tuple(bool, bool, bool, bool, bool, bool)

        """
        ret = await self.write_command("\6", multi_line=False)

        code = int(ret.decode())

        return tuple([(code & (1 << i)) > 0 for i in range(3)])

    async def controller_ready(self):
        """Generate requestControllerReadyStatus command string.

        (p. 141) Request Controller Ready Status Asks controller for ready
        status (tests if controller is ready to perform a new command)

        B1h (ASCII character 177) if controller is ready B0h (ASCII character
        176) if controller is not ready (e.g., performing a reference move)
        """
        ret = await self.write_command("\7", multi_line=False)

        comp = ret == chr(177)
        self.log.debug(f"{ret} : {chr(177)} : {comp}")

        return ret == chr(177)

    async def stop_all_axes(self):
        """Generate stopAllAxes command string.

        (p. 143) Stop All Axes To confirm that this worked, #5 has to be used.
        """
        return await self.write_command(chr(24), has_response=False)

    async def set_position(self, x=None, y=None, z=None,
                           u=None, v=None, w=None):
        """Generate setTargetPosition command string.

        (p. 206) Set Target Position

        :Execute:
        :Send: MOV X 10 U 5
        :Note: Axis X moves to 10 (target
        position in mm), axis U moves to
        5 (target position in deg)

        Parameters
        ----------
        x : `float`
            X-axis position (in mm).
        y : `float`
            Y-axis position (in mm).
        z : `float`
            Z-axis position (in mm).
        u : `float`
            U-axis rotation (in deg).
        v : `float`
            V-axis rotation (in deg).
        w : `float`
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

    async def referencing_result(self):
        """Generate getReferencingResult command string.

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
        """
        ret = await self.write_command("FRF?")

        return [float(val.split("=")[1]) == 1 for val in ret.decode().replace("\n", "").split(" ")]

    async def reference(self):
        """Perform a reference in all axes.
        """
        await self.write_command("FRF X Y Z U V W", has_response=False)

    async def target_position(self):
        """Generate getTargetPosition command string.

        (p. 208) Get Target Position

        MOV? gets the commanded positions. Use POS? (p. 216) to get the
        current positions.
        """
        ret = await self.write_command("MOV? X Y Z U V W")

        return [float(val.split("=")[1]) for val in ret.decode().replace("\n", "").split(" ")]

    async def set_low_position_soft_Limit(self, x=None, y=None, z=None, u=None, v=None, w=None):
        """Generate setLowPositionSoftLimit command string.

        (p. 212) Set Low Position Soft Limit

        Limits the low end of the axis travel range in closed-loop operation ("soft limit").
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        await self.write_command("NLM" + target, has_response=False)

    async def get_low_position_soft_limit(self):
        """Generate getLowPositionSoftLimit command string.

        Get the position "soft limit" which determines the low end of
        the axis travel range in closed-loop operation.
        """
        ret = await self.write_command("NLM? X Y Z U V W")

        return [float(val.split("=")[1]) for val in ret.decode().replace("\n", "").split(" ")]

    async def set_high_position_soft_limit(self, x=None, y=None, z=None, u=None, v=None, w=None):
        """Generate setHighPositionSoftLimit command string.

        (p. 214) Set High Position Soft Limit

        Limits the high end of the axis travel range in closed-loop
        operation ("soft limit").
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        await self.write_command("PLM" + target, has_response=False)

    async def get_high_position_soft_limit(self):
        """Get High Position Soft Limit."""
        ret = await self.write_command("PLM? X Y Z U V W")

        return [float(val.split("=")[1]) for val in ret.decode().replace("\n", "").split(" ")]

    async def on_target(self):
        """Generate getOnTargetState command string.

        (p. 213) Get On Target State

        Gets on-target state of given axis.

        if all arguments are omitted, gets state of all axes.
        """
        ret = await self.write_command("ONT?")

        return [float(val.split("=")[1]) == 1 for val in ret.decode().replace("\n", "").split(" ")]

    async def get_position_unit(self):
        """Generate getPositionUnit command string.

        (p. 217) Get Position Unit

        Get the current unit of the position.
        """
        ret = await self.write_command("PUN? X Y Z U V W")

        return [val.split("=")[1] for val in ret.decode().replace("\n", "").split(" ")]

    async def offset(self, x=None, y=None, z=None, u=None, v=None, w=None):
        """Generate setTargetRelativeToCurrentPosition command string.

        (p. 215) Set Target Relative To Current Position
        Moves given axes relative to the last commanded target position.
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        await self.write_command("MVR" + target)

    async def check_offset(self, x=None, y=None, z=None, u=None, v=None, w=None):
        """Generate virtualMove command string.

        (p. 253) VMO? (Virtual Move)

        Checks whether the moving platform of the Hexapod can approach
        a specified position from the current position.

        Used to validate if MVR command is possible.
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        ret = await self.write_command("VMO?" + target)

        return [float(val.split("=")[1]) == 1 for val in ret.decode().replace("\n", "").split(" ")]

    async def set_pivot_point(self, x=None, y=None, z=None):
        """Generate setPivotPoint command string.

        (p. 227)(Set Pivot Point)

        Sets the pivot point coordinates in the volatile memory.
        Can only be set when the following holds true for the rotation
        coordinates of the moving platform: U = V = W = 0
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""

        await self.write_command("SPI" + target, has_response=False)

    async def getPivotPoint(self):
        """Generate getPivotPoint command string.

        (p. 229) (Get Pivot Point)

        Gets the pivot point coordinates.
        """
        ret = await self.write_command("SPI?")

        return [float(val.split("=")[1]) for val in ret.decode().replace("\n", "").split(" ")]

    async def check_active_soft_limit(self):
        """Generate getSoftLimitStatus command string.

        SSL? (p. 230) Get Soft Limit Status
        """
        ret = await self.write_command("SSL?")

        return [float(val.split("=")[1]) == 1 for val in ret.decode().replace("\n", "").split(" ")]

    async def activate_soft_limit(self, x=True, y=True, z=True, u=True, v=True, w=True):
        """Generate setSoftLimit command string.

        (p. 229) Set Soft Limit

        Activates or deactivates the soft limits that are set with NLM (p. 212) and PLM (p. 214).

        Soft limits can only be activated/deactivated when the axis is not moving (query with #5 (p. 140)).
        """
        target = ""
        target += " X " + ("1" if x else "0")
        target += " Y " + ("1" if y else "0")
        target += " Z " + ("1" if z else "0")
        target += " U " + ("1" if u else "0")
        target += " V " + ("1" if v else "0")
        target += " W " + ("1" if w else "0")

        await self.write_command("SSL" + target, has_response=False)

    async def set_clv(self, x=None, y=None, z=None, u=None, v=None, w=None):
        """Generate setClosedLoopVelocity command string.

        (p. 243) (Set Closed-Loop Velocity)

        The velocity can be changed with VEL while the axis is moving.
        """
        target = ""
        target += " X " + str(float(x)) if x is not None else ""
        target += " Y " + str(float(y)) if y is not None else ""
        target += " Z " + str(float(z)) if z is not None else ""
        target += " U " + str(float(u)) if u is not None else ""
        target += " V " + str(float(v)) if v is not None else ""
        target += " W " + str(float(w)) if w is not None else ""

        await self.write_command("VEL" + target, has_response=False)

    async def get_clv(self):
        """Generate getClosedLoopVelocity command string.

        (p. 244) (Get Closed-Loop Velocity)

        If all arguments are omitted, the value of all axes commanded with VEL is queried.
        """
        ret = await self.write_command("VEL?")

        return [float(val.split("=")[1]) == 1 for val in ret.decode().replace("\n", "").split(" ")]

    async def set_sv(self, velocity):
        """Generate setSystemVelocity command string.

        (p. 251) (Set System Velocity)

        Sets the velocity for the moving platform of the Hexapod

        The velocity can only be set with VLS when the Hexapod
        is not moving (axes X, Y, Z, U, V, W; query with #5 (p. 140)).
        For axes A and B, the velocity can be set with VEL (p. 243).
        """
        await self.write_command(f"VLS {velocity}", has_response=False)

    async def get_sv(self):
        """Generate getSystemVelocity command string.

        (p. 252) Gets the velocity of the moving platform of the Hexapod that is set with VLS (p. 245).
        """
        return float(await self.write_command("VLS?"))

    async def get_error(self):
        """Generate getErrorNumber command string.

        (p. 163) Get Error Number

        Get error code of the last occurred error and reset the error to 0.
        """
        return int(await self.write_command("ERR?", multi_line=False))
