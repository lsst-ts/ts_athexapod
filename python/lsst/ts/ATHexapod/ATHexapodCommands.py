from enum import Enum

class ATHexapodCommand:

    hexapodAxis = ['X', 'Y', 'Z', 'U', 'V', 'W']

    def __init__(self):
        pass

    def getRealPosition(self):
        """
        (p. 138) Get Real Position.
        This command is identical in
        function to POS? (p. 216), but
        only one character has to be
        sent via the interface. Therefore
        #3 can also be used while the
        controller is performing timeconsuming
        tasks.
        Between the switching-on of the
        controller and the reference
        point definition of the Hexapod
        with FRF (p. 174), the current
        position of the Hexapod and
        axes A and B is unknown.
        Nevertheless, the response to
        #3 gives the position value 0 for
        all axes.
        """
        return "\3"


    def requestMotionStatus(self):
        """
        (p. 140) Request Motion Status.
        Axes 1 to 8 correspond to the X,
        Y, Z, U, V, W, A and B axes in
        this order. Exception: When the
        "NOSTAGE" stage type is
        assigned to an axis (possible for
        axes A and B; query with the
        CST? (p. 152) command), this
        axis is not included in the
        bitmapped answer. In this case,
        it is skipped when counting the
        axes.

        return:
        The answer <uint> is bit-mapped
        and returned as the hexadecimal
        sum of the following codes:
        1=first axis is moving
        2=second axis is moving
        4=third axis is moving ...
        """
        return "\5"


    def queryForPositionChange(self):
        """
        Queries wheter the axis positions have changed since the last position query was sent.
        Response:
        The response <uint> is bit-mappet and returned as the hexadecimal sum of the following codes:
        1 = Position of the first axis has changed
        2 = Position of the second axis has changed
        4 = Posiiton of the third axis has changed
        ...
        """
        return "\6"

    def requestControllerReadyStatus(self):
        """
        (p. 141) Request Controller
        Ready Status
        Asks controller for ready status
        (tests if controller is ready to
        perform a new command)

        B1h (ASCII character 177 = "±"
        in Windows) if controller is ready
        B0h (ASCII character 176 = "°"
        in Windows) if controller is not
        ready (e.g., performing a
        reference move)
        """
        return "\7"


    def stopAllAxes(self):
        """
        (p. 143) Stop All Axes
        To confirm that this worked, #5
        has to be used.

        Return: No return
        """
        return chr(24)


    def setTargetPosition(self, X: float = None, Y: float = None, Z: float = None, U: float = None, V: float = None, W: float = None):
        """
        (p. 206) Set Target Position
        Execute:

        Send: MOV X 10 U 5
        Note: Axis X moves to 10 (target
        position in mm), axis U moves to
        5 (target position in °)
        """
        target = ""
        target += " X " + str(float(X)) if X is not None else ""
        target += " Y " + str(float(Y)) if Y is not None else ""
        target += " Z " + str(float(Z)) if Z is not None else ""
        target += " U " + str(float(U)) if U is not None else ""
        target += " V " + str(float(V)) if V is not None else ""
        target += " W " + str(float(W)) if W is not None else ""
        return "MOV" + target

    def performsReference(self, X: bool = True, Y: bool = False, Z: bool = False, U: bool = False, V: bool = False, W: bool = False):
        """
        Performs a reference .
        Moves the given axis to the reference point switch and sets the current position to a defined value. See below for details.
        If Multiple axes are given in the command, they are moved synchronously.
        """
        target = ""
        target += " X " if X else ""
        target += " Y " if Y else ""
        target += " Z " if Z else ""
        target += " U " if U else ""
        target += " V " if V else ""
        target += " W " if W else ""
        return "FRF" + target

    def getTargetPosition(self):
        """
        (p. 208) Get Target Position

        MOV? gets the commanded positions. Use POS? (p. 216) to get the current positions.
        """
        return "MOV? X Y Z U V W"

    def setLowPositionSoftLimit(self, X: float = None, Y: float = None, Z: float = None, U: float = None, V: float = None, W: float = None):
        """
        (p. 212) Set Low Position Soft Limit

        Limits the low end of the axis travel range in closed-loop operation ("soft limit").
        """
        target = ""
        target += " X " + str(float(X)) if X is not None else ""
        target += " Y " + str(float(Y)) if Y is not None else ""
        target += " Z " + str(float(Z)) if Z is not None else ""
        target += " U " + str(float(U)) if U is not None else ""
        target += " V " + str(float(V)) if V is not None else ""
        target += " W " + str(float(W)) if W is not None else ""
        return "NLM" + target

    def getLowPositionSoftLimit(self):
        """
        Get the position "soft limit" which determines the low end of
        the axis travel range in closed-loop operation.
        """
        return "NLM? X Y Z U V W"

    def getOnTargetState(self):
        """
        (p. 213) Get On Target State

        Gets on-target state of given axis.

        if all arguments are omitted, gets state of all axes.
        """
        return "ONT?"

    def setHighPositionSoftLimit(self, X: float = None, Y: float = None, Z: float = None, U: float = None, V: float = None, W: float = None):
        """
        (p. 214) Set High Position Soft Limit

        Limits the high end of the axis travel range in closed-loop operation ("soft limit").
        """
        target = ""
        target += " X " + str(float(X)) if X is not None else ""
        target += " Y " + str(float(Y)) if Y is not None else ""
        target += " Z " + str(float(Z)) if Z is not None else ""
        target += " U " + str(float(U)) if U is not None else ""
        target += " V " + str(float(V)) if V is not None else ""
        target += " W " + str(float(W)) if W is not None else ""
        return "PLM" + target

    def getHighPositionSoftLimit(self):
        """
        Get High Position Soft Limit
        """
        return "PLM? X Y Z U V W"

    def getPositionUnit(self):
        """
        (p. 217) Get Position Unit
        Gets the current unit of the position. If all arguments are omitted, gets current unit of the position for all axes.
        """
        return "PUN? X Y Z U V W"

    def setTargetRelativeToCurrentPosition(self, X: float = None, Y: float = None, Z: float = None, U: float = None, V: float = None, W: float = None):
        """
        (p. 215) Set Target Relative To Current Position
        Moves given axes relative to the last commanded target position.
        """
        target = ""
        target += " X " + str(float(X)) if X is not None else ""
        target += " Y " + str(float(Y)) if Y is not None else ""
        target += " Z " + str(float(Z)) if Z is not None else ""
        target += " U " + str(float(U)) if U is not None else ""
        target += " V " + str(float(V)) if V is not None else ""
        target += " W " + str(float(W)) if W is not None else ""
        return "MVR"+target

    def virtualMove(self, X: float = None, Y: float = None, Z: float = None, U: float = None, V: float = None, W: float = None):
        """
        (p. 253) VMO? (Virtual Move)

        Checks whether the moving platform of the Hexapod can approach a specified position from the current position.

        Used to validate if MVR command is possible.
        """
        target = ""
        target += " X " + str(float(X)) if X is not None else ""
        target += " Y " + str(float(Y)) if Y is not None else ""
        target += " Z " + str(float(Z)) if Z is not None else ""
        target += " U " + str(float(U)) if U is not None else ""
        target += " V " + str(float(V)) if V is not None else ""
        target += " W " + str(float(W)) if W is not None else ""
        return "VMO?"+target

    def setPivotPoint(self, X: float = None, Y: float = None, Z: float = None):
        """
        (p. 227)(Set Pivot Point)

        Sets the pivot point coordinates in the volatile memory. Can only be set when the following holds true for the rotation coordinates of the moving platform: U = V = W = 0
        """
        target = ""
        target += " X " + str(float(X)) if X is not None else ""
        target += " Y " + str(float(Y)) if Y is not None else ""
        target += " Z " + str(float(Z)) if Z is not None else ""
        return "SPI"+target

    def getPivotPoint(self):
        """
        (p. 229) (Get Pivot Point)

        Gets the pivot point coordinates.
        """
        return "SPI?"

    def getSoftLimitStatus(self):
        """
        SSL? (p. 230) Get Soft Limit Status
        """
        return "SSL?"

    def setSoftLimit(self, X: bool = None, Y: bool = None, Z: bool = None, U: bool = None, V: bool = None, W: bool = None):
        """
        (p. 229) Set Soft Limit

        Activates or deactivates the soft limits that are set with NLM (p. 212) and PLM (p. 214).

        Soft limits can only be activated/deactivated when the axis is not moving (query with #5 (p. 140)).
        """
        target = ""
        target += " X " + ("1" if X else "0")
        target += " Y " + ("1" if Y else "0")
        target += " Z " + ("1" if Z else "0")
        target += " U " + ("1" if U else "0")
        target += " V " + ("1" if V else "0")
        target += " W " + ("1" if W else "0")
        return "SSL"+target

    def setClosedLoopVelocity(self, X: float = None, Y: float = None, Z: float = None, U: float = None, V: float = None, W: float = None):
        """
        (p. 243) (Set Closed-Loop Velocity)

        The velocity can be changed with VEL while the axis is moving.
        """
        target = ""
        target += " X " + str(float(X)) if X is not None else ""
        target += " Y " + str(float(Y)) if Y is not None else ""
        target += " Z " + str(float(Z)) if Z is not None else ""
        target += " U " + str(float(U)) if U is not None else ""
        target += " V " + str(float(V)) if V is not None else ""
        target += " W " + str(float(W)) if W is not None else ""
        return "VEL"+target

    def getClosedLoopVelocity(self):
        """
        (p. 244) (Get Closed-Loop Velocity)

        If all arguments are omitted, the value of all axes commanded with VEL is queried.
        """
        return "VEL?"

    def setSystemVelocity(self, velocity):
        """
         (p. 251) (Set System Velocity)

        Sets the velocity for the moving platform of the Hexapod

        The velocity can only be set with VLS when the Hexapod is not moving (axes X, Y, Z, U, V, W; query with #5 (p. 140)). For axes A and B, the velocity can be set with VEL (p. 243).
        """
        velocity = float(velocity)
        return "VLS "+str(velocity)

    def getSystemVelocity(self):
        """
        (p. 252) Gets the velocity of the moving platform of the Hexapod that is set with VLS (p. 245).
        """
        return "VLS?"

    def getErrorNumber(self):
        """
        (p. 163) Get Error Number

        Get error code of the last occurred error and reset the error to 0.
        """
        return "ERR?"
