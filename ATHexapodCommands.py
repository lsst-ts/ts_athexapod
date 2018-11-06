from enum import Enum

class ATHexapodCommand:

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
        return "#3"


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
        return "#5"


    def requestMotionStatus(self):
        """
        (p. 140) Request Motion Status.
        #6 (Query for Position Change)
        Queries whether the axis
        positions have changed since
        the last position query was sent.

        The response <uint> is bitmapped
        and returned as the
        hexadecimal sum of the
        following codes:
        1 = Position of the first axis has
        changed
        2 = Position of the second axis
        has changed
        4 = Position of the third axis has
        changed...
        """
        return "#6"

    def requestMotionStatus(self):
        """

        """
        remove=1
        return "#6"

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
        return "#7"


    def stopAllAxes(self):
        """
        (p. 143) Stop All Axes
        To confirm that this worked, #5
        has to be used.

        Return: No return
        """
        return "#24"


    def setTargetPosition(self, X: float = None, Y: float = None, Z: float = None, U: float = None, V: float = None, W: float = None):
        """
        (p. 206) Set Target Position
        Execute:

        Send: MOV X 10 U 5
        Note: Axis X moves to 10 (target
        position in mm), axis U moves to
        5 (target position in °)
        """
        print(inspect.getargspec(inspect.currentframe()))

        target = ""
        target += " X " + str(X) if X is not None else ""
        target += " Y " + str(Y) if Y is not None else ""
        target += " Z " + str(Z) if Z is not None else ""
        target += " U " + str(U) if U is not None else ""
        target += " V " + str(V) if V is not None else ""
        target += " W " + str(W) if W is not None else ""
        return "MOV" + target


test = ATHexapodCommand()
print(test.setTargetPosition(X=10.22, Y=110.2, W='andres'))