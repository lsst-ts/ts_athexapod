
__all__ = ['Model']

import logging

from .controller import ATHexapodController


class Model:

    def __init__(self, log=None):

        self.log = log

        if self.log is None:
            self.log = logging.getLogger(__name__)

        self.controller = ATHexapodController(log=log)

    def is_connected(self):
        """ Check if connected to the controller.

        Returns
        -------
        connected : bool

        """
        return self.controller.is_connected()

    async def connect(self):
        """ Connect to hexapod controller.
        """

        await self.controller.connect()

    async def disconnect(self):
        """ Disconnect from hexapod controller.
        """

        await self.controller.disconnect()

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

        return await self.controller.write_command(cmd, has_response, multi_line)

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
        return await self.controller.real_position()

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
        return await self.controller.motion_status()

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
        return await self.controller.position_changed()

    async def controller_ready(self):
        """Generate requestControllerReadyStatus command string.

        (p. 141) Request Controller Ready Status Asks controller for ready
        status (tests if controller is ready to perform a new command)

        B1h (ASCII character 177) if controller is ready B0h (ASCII character
        176) if controller is not ready (e.g., performing a reference move)
        """
        return await self.controller.controller_ready()

    async def stop_all_axes(self):
        """Generate stopAllAxes command string.

        (p. 143) Stop All Axes To confirm that this worked, #5 has to be used.
        """
        return await self.controller.stop_all_axes()

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
        await self.controller.set_position(x, y, z, u, v, w)

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
        return await self.controller.referencing_result()

    async def reference(self):
        """Perform a reference in all axes.
        """
        return await self.controller.reference()

    async def target_position(self):
        """Generate getTargetPosition command string.

        (p. 208) Get Target Position

        MOV? gets the commanded positions. Use POS? (p. 216) to get the
        current positions.
        """
        return await self.controller.target_position()

    async def set_low_position_soft_Limit(self, x=None, y=None, z=None, u=None, v=None, w=None):
        """Generate setLowPositionSoftLimit command string.

        (p. 212) Set Low Position Soft Limit

        Limits the low end of the axis travel range in closed-loop operation ("soft limit").
        """
        return await self.controller.set_low_position_soft_Limit(x, y, z, u, v, w)

    async def get_low_position_soft_limit(self):
        """Generate getLowPositionSoftLimit command string.

        Get the position "soft limit" which determines the low end of
        the axis travel range in closed-loop operation.
        """
        return await self.controller.get_low_position_soft_limit()

    async def set_high_position_soft_limit(self, x=None, y=None, z=None, u=None, v=None, w=None):
        """Generate setHighPositionSoftLimit command string.

        (p. 214) Set High Position Soft Limit

        Limits the high end of the axis travel range in closed-loop
        operation ("soft limit").
        """
        return await self.controller.set_high_position_soft_limit(x, y, z, u, v, w)

    async def get_high_position_soft_limit(self):
        """Get High Position Soft Limit."""
        return await self.controller.get_high_position_soft_limit()

    async def on_target(self):
        """Generate getOnTargetState command string.

        (p. 213) Get On Target State

        Gets on-target state of given axis.

        if all arguments are omitted, gets state of all axes.
        """
        return await self.controller.on_target()

    async def get_position_unit(self):
        """Generate getPositionUnit command string.

        (p. 217) Get Position Unit

        Get the current unit of the position.
        """
        return await self.controller.get_position_unit()

    async def offset(self, x=None, y=None, z=None, u=None, v=None, w=None):
        """Generate setTargetRelativeToCurrentPosition command string.

        (p. 215) Set Target Relative To Current Position
        Moves given axes relative to the last commanded target position.
        """
        await self.controller.offset(x, y, z, u, v, w)

    async def check_offset(self, x=None, y=None, z=None, u=None, v=None, w=None):
        """Generate virtualMove command string.

        (p. 253) VMO? (Virtual Move)

        Checks whether the moving platform of the Hexapod can approach
        a specified position from the current position.

        Used to validate if MVR command is possible.
        """
        return await self.controller.check_offset(x, y, z, u, v, w)

    async def set_pivot_point(self, x=None, y=None, z=None):
        """Generate setPivotPoint command string.

        (p. 227)(Set Pivot Point)

        Sets the pivot point coordinates in the volatile memory.
        Can only be set when the following holds true for the rotation
        coordinates of the moving platform: U = V = W = 0
        """
        await self.controller.set_pivot_point(x, y, z)

    async def getPivotPoint(self):
        """Generate getPivotPoint command string.

        (p. 229) (Get Pivot Point)

        Gets the pivot point coordinates.
        """
        return await self.controller.getPivotPoint()

    async def check_active_soft_limit(self):
        """Generate getSoftLimitStatus command string.

        SSL? (p. 230) Get Soft Limit Status
        """
        return await self.controller.check_active_soft_limit()

    async def activate_soft_limit(self, x=True, y=True, z=True, u=True, v=True, w=True):
        """Generate setSoftLimit command string.

        (p. 229) Set Soft Limit

        Activates or deactivates the soft limits that are set with NLM (p. 212) and PLM (p. 214).

        Soft limits can only be activated/deactivated when the axis is not moving (query with #5 (p. 140)).
        """
        await self.controller.activate_soft_limit(x, y, z, u, v, w)

    async def set_clv(self, x=None, y=None, z=None, u=None, v=None, w=None):
        """Generate setClosedLoopVelocity command string.

        (p. 243) (Set Closed-Loop Velocity)

        The velocity can be changed with VEL while the axis is moving.
        """
        await self.controller.set_clv(x, y, z, u, v, w)

    async def get_clv(self):
        """Generate getClosedLoopVelocity command string.

        (p. 244) (Get Closed-Loop Velocity)

        If all arguments are omitted, the value of all axes commanded with VEL is queried.
        """
        return await self.controller.get_clv()

    async def set_sv(self, velocity):
        """Generate setSystemVelocity command string.

         (p. 251) (Set System Velocity)

        Sets the velocity for the moving platform of the Hexapod

        The velocity can only be set with VLS when the Hexapod
        is not moving (axes X, Y, Z, U, V, W; query with #5 (p. 140)).
        For axes A and B, the velocity can be set with VEL (p. 243).
        """
        await self.controller.set_sv(velocity)

    async def get_sv(self):
        """Generate getSystemVelocity command string.

        (p. 252) Gets the velocity of the moving platform of the Hexapod that is set with VLS (p. 245).
        """
        return await self.controller.get_sv()

    async def get_error(self):
        """Generate getErrorNumber command string.

        (p. 163) Get Error Number

        Get error code of the last occurred error and reset the error to 0.
        """
        return await self.controller.get_error()
