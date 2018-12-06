__all__ = ["ATHexapodController"]

from .ATHexapodCommands import ATHexapodCommand
from lsst.ts.pythonCommunicator.TcpCommunicator import TcpClient, TCPEndStr


class ATHexapodController:
    def __init__(self):
        self.hexc = ATHexapodCommand()
        self.controllerReady = False
        self.communicator = None

    def configureCommunicator(self, address, port, connectTimeout=2, readTimeout=2, sendTimeout=2,
                              endStr='\n', maxLength=1024):
        """
        Configure communication protocol
        """
        messageHandler = TCPEndStr(endStr, maxLength)
        self.communicator = TcpClient(address, port, connectTimeout, readTimeout, sendTimeout,
                                      messageHandler=messageHandler)

    def connect(self):
        """
        connect to the hexapod
        """
        self.communicator.connect()

    def disconnect(self):
        """
        disconnect from the hexapod
        """
        self.communicator.disconnect()

    def moveToPosition(self, X: float = None, Y: float = None, Z: float = None,
                       U: float = None, V: float = None, W: float = None):
        """
        move to position
        use setTargetPosition
        """
        self.communicator.sendMessage(self.hexc.setTargetPosition(X, Y, Z, U, V, W))

    def setSystemVelocity(self, systemVelocity: float = None):
        """
        set system velocity
        use setSystemVelocity
        """
        self.communicator.sendMessage(self.hexc.setSystemVelocity(systemVelocity))

    def setPositionLimits(self, minPositionX=None, minPositionY=None, minPositionZ=None,
                          minPositionU=None, minPositionV=None, minPositionW=None,
                          maxPositionX=None, maxPositionY=None, maxPositionZ=None,
                          maxPositionU=None, maxPositionV=None, maxPositionW=None):
        """
        set position limits
        use setSystemVelocity
        """
        self.communicator.sendMessage(self.hexc.setLowPositionSoftLimit(
            minPositionX, minPositionY, minPositionZ, minPositionU, minPositionV, minPositionW))
        self.communicator.sendMessage(self.hexc.setHighPositionSoftLimit(
            maxPositionX, maxPositionY, maxPositionZ, maxPositionU, maxPositionV, maxPositionW))

    def initializePosition(self, X: bool = True, Y: bool = False, Z: bool = False,
                           U: bool = False, V: bool = False, W: bool = False):
        """
        set reference position to the device
        use performsReference
        """
        self.communicator.sendMessage(self.hexc.performsReference(X, Y, Z, U, V, W))

    def moveOffset(self, dX: float = None, dY: float = None, dZ: float = None,
                   dU: float = None, dV: float = None, dW: float = None):
        """
        move position by a relative position (related to current)
        use setTargetPosition
        """
        self.communicator.sendMessage(self.hexc.setTargetRelativeToCurrentPosition(dX, dY, dZ, dU, dV, dW))

    def getErrors(self):
        """
        get error codes from the hardware as a list
        It looks for errors until there's no error in the device
        Maximum of 10 tries
        use getErrorNumber
        """
        errors = []
        for i in range(10):
            self.communicator.sendMessage(self.hexc.getErrorNumber())
            errorNumber = int(self.communicator.getMessage())
            if errorNumber == 0:
                break
            errors.append(errorNumber)
        return errors

    def setPivot(self, X: float = None, Y: float = None, Z: float = None):
        """
        set pivot on the device
        use setPivotPoint
        """
        self.communicator.sendMessage(self.hexc.setPivotPoint(X, Y, Z))

    def getPivot(self):
        """
        get pivot on the device
        use getPivotPoint
        """
        self.communicator.sendMessage(self.hexc.getPivotPoint())
        axis1, pivotX = self.communicator.getMessage().split("=")
        axis2, pivotY = self.communicator.getMessage().split("=")
        axis3, pivotZ = self.communicator.getMessage().split("=")
        return [float(pivotX), float(pivotY), float(pivotZ)]

    def setSoftLimit(self, X: bool = None, Y: bool = None, Z: bool = None,
                     U: bool = None, V: bool = None, W: bool = None):
        """
        Activate software limits
        """
        self.communicator.sendMessage(self.hexc.setSoftLimit(X, Y, Z, U, V, W))

    def setSoftLimitStatus(self, X: bool = None, Y: bool = None, Z: bool = None,
                           U: bool = None, V: bool = None, W: bool = None):
        """
        Get software limits status
        """
        self.communicator.sendMessage(self.hexc.setSoftLimit(X, Y, Z, U, V, W))

    def getSoftLimitStatus(self):
        """
        Get software limits status
        """
        self.communicator.sendMessage(self.hexc.getSoftLimitStatus())
        axis1, x = self.communicator.getMessage().split("=")
        axis2, y = self.communicator.getMessage().split("=")
        axis3, z = self.communicator.getMessage().split("=")
        axis4, u = self.communicator.getMessage().split("=")
        axis5, v = self.communicator.getMessage().split("=")
        axis6, w = self.communicator.getMessage().split("=")
        return bool(int(x)), bool(int(y)), bool(int(z)), bool(int(u)), bool(int(v)), bool(int(w))

    def stopMotion(self):
        """
        stop all motion
        use stopAllAxes
        """
        self.communicator.sendMessage(self.hexc.stopAllAxes())

    def validPosition(self, X: float = None, Y: float = None, Z: float = None,
                      U: float = None, V: float = None, W: float = None):
        """
        Check if position commanded can be reached.
        Return True if possible and False if not
        use virtualMove
        """
        self.communicator.sendMessage(self.hexc.virtualMove(X, Y, Z, U, V, W))
        return bool(int(self.communicator.getMessage()))

    def getTargetPositions(self):
        """
        Function in charge to query positions
        """
        self.communicator.sendMessage(self.hexc.getTargetPosition())
        axis1, x = self.communicator.getMessage().split("=")
        axis2, y = self.communicator.getMessage().split("=")
        axis3, z = self.communicator.getMessage().split("=")
        axis4, u = self.communicator.getMessage().split("=")
        axis5, v = self.communicator.getMessage().split("=")
        axis6, w = self.communicator.getMessage().split("=")

        return float(x), float(y), float(z), float(u), float(v), float(w)

    def getUnits(self):
        """
        Get positions unit
        :return:
        """
        self.communicator.sendMessage(self.hexc.getPositionUnit())
        axis1, xunit = self.communicator.getMessage().split("=")
        axis2, yunit = self.communicator.getMessage().split("=")
        axis3, zunit = self.communicator.getMessage().split("=")
        axis4, uunit = self.communicator.getMessage().split("=")
        axis5, vunit = self.communicator.getMessage().split("=")
        axis6, wunit = self.communicator.getMessage().split("=")
        return [xunit, yunit, zunit, uunit, vunit, wunit]

    def getRealPositions(self):
        """
        Function in charge to query the actual positions of the hexapod
        """
        self.communicator.sendMessage(self.hexc.getRealPosition())
        axis1, x = self.communicator.getMessage().split("=")
        axis2, y = self.communicator.getMessage().split("=")
        axis3, z = self.communicator.getMessage().split("=")
        axis4, u = self.communicator.getMessage().split("=")
        axis5, v = self.communicator.getMessage().split("=")
        axis6, w = self.communicator.getMessage().split("=")

        return float(x), float(y), float(z), float(u), float(v), float(w)

    def getLowLimits(self):
        """
        get current low positions limits
        """
        self.communicator.sendMessage(self.hexc.getLowPositionSoftLimit())
        axis1, x = self.communicator.getMessage().split("=")
        axis2, y = self.communicator.getMessage().split("=")
        axis3, z = self.communicator.getMessage().split("=")
        axis4, u = self.communicator.getMessage().split("=")
        axis5, v = self.communicator.getMessage().split("=")
        axis6, w = self.communicator.getMessage().split("=")

        return float(x), float(y), float(z), float(u), float(v), float(w)

    def getHighLimits(self):
        """
        Update current high positions limits
        """
        self.communicator.sendMessage(self.hexc.getHighPositionSoftLimit())
        axis1, x = str(self.communicator.getMessage()).split("=")
        axis2, y = str(self.communicator.getMessage()).split("=")
        axis3, z = str(self.communicator.getMessage()).split("=")
        axis4, u = str(self.communicator.getMessage()).split("=")
        axis5, v = str(self.communicator.getMessage()).split("=")
        axis6, w = str(self.communicator.getMessage()).split("=")

        return float(x), float(y), float(z), float(u), float(v), float(w)

    def getSystemVelocity(self):
        """
        get current system velocity
        """
        self.communicator.sendMessage(self.hexc.getSystemVelocity())
        systemVelocity = float(self.communicator.getMessage())
        return systemVelocity

    def getOnTargetState(self):
        """
        Returns true if it is on Target
        """
        self.communicator.sendMessage(self.hexc.getOnTargetState())
        Axis1, onTargetX = str(self.communicator.getMessage()).split("=")
        Axis2, onTargetY = str(self.communicator.getMessage()).split("=")
        Axis3, onTargetZ = str(self.communicator.getMessage()).split("=")
        Axis4, onTargetU = str(self.communicator.getMessage()).split("=")
        Axis5, onTargetV = str(self.communicator.getMessage()).split("=")
        Axis6, onTargetW = str(self.communicator.getMessage()).split("=")
        return (bool(int(onTargetX)), bool(int(onTargetY)), bool(int(onTargetZ)),
                bool(int(onTargetU)), bool(int(onTargetV)), bool(int(onTargetW)))

    def getMotionStatus(self):
        """
        Returns motion status in order X, Y, Z, U, V, W, A, B
        where True means it's moving and False for not moving
        """
        self.communicator.sendMessage(self.hexc.requestMotionStatus())
        result = int(self.communicator.getMessage())
        status = '{0:08b}'.format(result)
        return (bool(status[7]), bool(status[6]), bool(status[5]), bool(status[4]),
                bool(status[3]), bool(status[2]), bool(status[1]), bool(status[0]))

    def getPositionChangeStatus(self):
        """
        Returns position change status for X, Y, Z, U, V, W, A, B
        where True means it's position has changed since last query
        """
        self.communicator.sendMessage(self.hexc.queryForPositionChange())
        result = int(self.communicator.getMessage())
        status = '{0:08b}'.format(result)
        return (bool(status[7]), bool(status[6]), bool(status[5]), bool(status[4]),
                bool(status[3]), bool(status[2]), bool(status[1]), bool(status[0]))

    def getReadyStatus(self):
        """
        Check if the hardware is ready to get commands, and update
        current class variable  'self.controllerReady' accordingly
        """
        self.communicator.sendMessage(self.hexc.requestControllerReadyStatus())
        ready = self.communicator.getMessage() == "±"
        if ready == 1:
            return True
        else:
            return False


class ATHexapodPosition:

    def __init__(self):
        self.pivotX = 0.0
        self.pivotY = 0.0
        self.pivotZ = 0.0

        self.positionX = 0.0
        self.positionY = 0.0
        self.positionZ = 0.0
        self.positionU = 0.0
        self.positionV = 0.0
        self.positionW = 0.0

        self.maxPositionX = 10.0
        self.maxPositionY = 10.0
        self.maxPositionZ = 10.0
        self.maxPositionU = 10.0
        self.maxPositionV = 10.0
        self.maxPositionW = 10.0

        self.minPositionX = -10.0
        self.minPositionY = -10.0
        self.minPositionZ = -10.0
        self.minPositionU = -10.0
        self.minPositionV = -10.0
        self.minPositionW = -10.0

        self.systemVelocity = 0

    def updateLimits(self, minPositionX=None, minPositionY=None, minPositionZ=None,
                     minPositionU=None, minPositionV=None, minPositionW=None,
                     maxPositionX=None, maxPositionY=None, maxPositionZ=None,
                     maxPositionU=None, maxPositionV=None, maxPositionW=None):
        if (maxPositionX is not None):
            self.maxPositionX = float(maxPositionX)
        if (maxPositionY is not None):
            self.maxPositionY = float(maxPositionY)
        if (maxPositionZ is not None):
            self.maxPositionZ = float(maxPositionZ)
        if (maxPositionU is not None):
            self.maxPositionU = float(maxPositionU)
        if (maxPositionV is not None):
            self.maxPositionV = float(maxPositionV)
        if (maxPositionW is not None):
            self.maxPositionW = float(maxPositionW)

        if (minPositionX is not None):
            self.minPositionX = float(minPositionX)
        if (minPositionY is not None):
            self.minPositionY = float(minPositionY)
        if (minPositionZ is not None):
            self.minPositionZ = float(minPositionZ)
        if (minPositionU is not None):
            self.minPositionU = float(minPositionU)
        if (minPositionV is not None):
            self.minPositionV = float(minPositionV)
        if (minPositionW is not None):
            self.minPositionW = float(minPositionW)

    def getLimits(self):
        return [self.maxPositionX, self.maxPositionY, self.maxPositionZ,
                self.maxPositionU, self.maxPositionV, self.maxPositionW,
                self.minPositionX, self.minPositionY, self.minPositionZ,
                self.minPositionU, self.minPositionV, self.minPositionW]

    def updatePosition(self, positionX=None, positionY=None, positionZ=None,
                       positionU=None, positionV=None, positionW=None):
        if (positionX is not None):
            self.positionX = float(positionX)
        if (positionY is not None):
            self.positionY = float(positionY)
        if (positionZ is not None):
            self.positionZ = float(positionZ)
        if (positionU is not None):
            self.positionU = float(positionU)
        if (positionV is not None):
            self.positionV = float(positionV)
        if (positionW is not None):
            self.positionW = float(positionW)

    def updatePivot(self, pivotX=None, pivotY=None, pivotZ=None):
        if(pivotX is not None):
            self.pivotX = float(pivotX)

        if(pivotY is not None):
            self.pivotY = float(pivotY)

        if(pivotZ is not None):
            self.pivotZ = float(pivotZ)

    def updateSystemVelocity(self, systemVelocity=None):
        if systemVelocity is not None:
            self.systemVelocity = float(systemVelocity)

    def getPosition(self):
        """
        :return: Current position
        """
        return [self.positionX, self.positionY, self.positionZ,
                self.positionU, self.positionV, self.positionW]

    def getPivot(self):
        return [self.pivotX, self.pivotY, self.pivotZ]

    def getSystemVelocity(self):
        return self.systemVelocity
