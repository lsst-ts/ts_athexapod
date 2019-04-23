__all__ = ["ATHexapodController"]

from lsst.ts.ATHexapod.ATHexapodCommands import ATHexapodCommand
from lsst.ts.pythonCommunicator.TcpCommunicator import TcpClientAsync, TCPEndStrAsync
from lsst.ts.pipython import gcserror
from functools import wraps
import time
import asyncio


class ATHexapodController:
    def __init__(self):
        self.hexc = ATHexapodCommand()
        self.controllerReady = False
        self.communicator = None
        self.lock = asyncio.Lock()

    def checkForRun(f):
        """Check if another task is running and wait until it finishes

        Arguments:
            f {function} -- Input function

        Returns:
            [function] -- Return the function to execute
        """
        @wraps(f)
        async def wrapper(self, *args, **kwargs):
            await self.lock.acquire()
            try:
                ret = await f(self, *args, **kwargs)
            finally:
                self.lock.release()
            return ret
        return wrapper

    def configureCommunicator(self, address, port, connectTimeout=2, readTimeout=2, sendTimeout=2,
                              endStr='\n', maxLength=1024):
        """
        Configure communication protocol
        """
        messageHandler = TCPEndStrAsync(endStr, maxLength)
        self.communicator = TcpClientAsync(address, port, connectTimeout, readTimeout, sendTimeout,
                                           messageHandler=messageHandler)

    @checkForRun
    async def connect(self):
        """
        connect to the hexapod
        """
        if(self.communicator.connected):
            await self.communicator.disconnect()
        await self.communicator.connect()

    @checkForRun
    async def disconnect(self):
        """
        disconnect from the hexapod
        """
        await self.communicator.disconnect()

    @checkForRun
    async def moveToPosition(self, X: float=None, Y: float=None, Z: float=None,
                             U: float=None, V: float=None, W: float=None):
        """
        move to position
        use setTargetPosition
        """
        await self.communicator.sendMessage(self.hexc.setTargetPosition(X, Y, Z, U, V, W))
        await self.checkErrors()

    @checkForRun
    async def setSystemVelocity(self, systemVelocity: float=None):
        """
        set system velocity
        use setSystemVelocity
        """
        await self.communicator.sendMessage(self.hexc.setSystemVelocity(systemVelocity))
        await self.checkErrors()

    @checkForRun
    async def setPositionLimits(self, minPositionX=None, minPositionY=None, minPositionZ=None,
                                minPositionU=None, minPositionV=None, minPositionW=None,
                                maxPositionX=None, maxPositionY=None, maxPositionZ=None,
                                maxPositionU=None, maxPositionV=None, maxPositionW=None):
        """
        set position limits
        use setSystemVelocity
        """
        if (minPositionU is not None) or (minPositionY is not None) or (minPositionZ is not None) \
                or (minPositionU is not None) or (minPositionV is not None) or (minPositionW is not None):
            await self.communicator.sendMessage(self.hexc.setLowPositionSoftLimit(
                minPositionX, minPositionY, minPositionZ, minPositionU, minPositionV, minPositionW))
            await self.checkErrors()

        if (maxPositionX is not None) or (maxPositionY is not None) or (maxPositionZ is not None) \
                or (maxPositionU is not None) or (maxPositionV is not None) or (maxPositionW is not None):
            await self.communicator.sendMessage(self.hexc.setHighPositionSoftLimit(
                maxPositionX, maxPositionY, maxPositionZ, maxPositionU, maxPositionV, maxPositionW))
            await self.checkErrors()

    @checkForRun
    async def initializePosition(self, X: bool=True, Y: bool=False, Z: bool=False,
                                 U: bool=False, V: bool=False, W: bool=False):
        """
        set reference position to the device
        use performsReference
        """
        await self.communicator.sendMessage(self.hexc.performsReference(X, Y, Z, U, V, W))
        await self.checkErrors()

    @checkForRun
    async def moveOffset(self, dX: float=None, dY: float=None, dZ: float=None,
                         dU: float=None, dV: float=None, dW: float=None):
        """
        move position by a relative position (related to current)
        use setTargetPosition
        """
        await self.communicator.sendMessage(self.hexc.setTargetRelativeToCurrentPosition(dX, dY, dZ, dU, dV,
                                            dW))
        await self.checkErrors()

    async def checkErrors(self):
        """
        get error codes from the hardware as a list
        It looks for errors until there's no error in the device
        Maximum of 10 tries
        use getErrorNumber
        """
        errors = []
        await self.communicator.sendMessage(self.hexc.getErrorNumber())
        result = await self.communicator.getMessage()
        errorNumber = int(result)
        noError = [0, 10]
        if errorNumber in noError:
            return errorNumber
        raise(Exception(gcserror.translate_error(value=errorNumber)))

    @checkForRun
    async def setPivot(self, X: float=None, Y: float=None, Z: float=None):
        """
        set pivot on the device
        use setPivotPoint
        """
        await self.communicator.sendMessage(self.hexc.setPivotPoint(X, Y, Z))
        await self.checkErrors()

    @checkForRun
    async def getPivot(self):
        """
        get pivot on the device
        use getPivotPoint
        """
        await self.communicator.sendMessage(self.hexc.getPivotPoint())
        axis1, pivotX = str(await self.communicator.getMessage()).split("=")
        axis2, pivotY = str(await self.communicator.getMessage()).split("=")
        axis3, pivotZ = str(await self.communicator.getMessage()).split("=")
        return float(pivotX), float(pivotY), float(pivotZ)

    @checkForRun
    async def setSoftLimit(self, X: bool=None, Y: bool=None, Z: bool=None,
                           U: bool=None, V: bool=None, W: bool=None):
        """
        Activate software limits
        """
        await self.communicator.sendMessage(self.hexc.setSoftLimit(X, Y, Z, U, V, W))
        await self.checkErrors()

    @checkForRun
    async def setSoftLimitStatus(self, X: bool=None, Y: bool=None, Z: bool=None,
                                 U: bool=None, V: bool=None, W: bool=None):
        """
        Get software limits status
        """
        await self.communicator.sendMessage(self.hexc.setSoftLimit(X, Y, Z, U, V, W))
        await self.checkErrors()

    @checkForRun
    async def getSoftLimitStatus(self):
        """
        Get software limits status
        """
        await self.communicator.sendMessage(self.hexc.getSoftLimitStatus())
        axis1, x = str(await self.communicator.getMessage()).split("=")
        axis2, y = str(await self.communicator.getMessage()).split("=")
        axis3, z = str(await self.communicator.getMessage()).split("=")
        axis4, u = str(await self.communicator.getMessage()).split("=")
        axis5, v = str(await self.communicator.getMessage()).split("=")
        axis6, w = str(await self.communicator.getMessage()).split("=")
        return bool(int(x)), bool(int(y)), bool(int(z)), bool(int(u)), bool(int(v)), bool(int(w))

    @checkForRun
    async def stopMotion(self):
        """
        stop all motion
        use stopAllAxes
        """
        await self.communicator.sendMessage(self.hexc.stopAllAxes())
        await self.checkErrors()

    @checkForRun
    async def validPosition(self, X: float=None, Y: float=None, Z: float=None,
                            U: float=None, V: float=None, W: float=None):
        """
        Check if position commanded can be reached.
        Return True if possible and False if not
        use virtualMove
        """
        await self.communicator.sendMessage(self.hexc.virtualMove(X, Y, Z, U, V, W))
        return bool(int(await self.communicator.getMessage()))

    @checkForRun
    async def getTargetPositions(self):
        """
        Function in charge to query positions
        """
        await self.communicator.sendMessage(self.hexc.getTargetPosition())
        axis1, x = str(await self.communicator.getMessage()).split("=")
        axis2, y = str(await self.communicator.getMessage()).split("=")
        axis3, z = str(await self.communicator.getMessage()).split("=")
        axis4, u = str(await self.communicator.getMessage()).split("=")
        axis5, v = str(await self.communicator.getMessage()).split("=")
        axis6, w = str(await self.communicator.getMessage()).split("=")

        return float(x), float(y), float(z), float(u), float(v), float(w)

    @checkForRun
    async def getUnits(self):
        """
        Get positions unit
        :return:
        """
        await self.communicator.sendMessage(self.hexc.getPositionUnit())
        axis1, xunit = str(await self.communicator.getMessage()).split("=")
        axis2, yunit = str(await self.communicator.getMessage()).split("=")
        axis3, zunit = str(await self.communicator.getMessage()).split("=")
        axis4, uunit = str(await self.communicator.getMessage()).split("=")
        axis5, vunit = str(await self.communicator.getMessage()).split("=")
        axis6, wunit = str(await self.communicator.getMessage()).split("=")
        return xunit, yunit, zunit, uunit, vunit, wunit

    @checkForRun
    async def getRealPositions(self):
        """
        Function in charge to query the actual positions of the hexapod
        """
        await self.communicator.sendMessage(self.hexc.getRealPosition())
        axis1, x = str(await self.communicator.getMessage()).split("=")
        axis2, y = str(await self.communicator.getMessage()).split("=")
        axis3, z = str(await self.communicator.getMessage()).split("=")
        axis4, u = str(await self.communicator.getMessage()).split("=")
        axis5, v = str(await self.communicator.getMessage()).split("=")
        axis6, w = str(await self.communicator.getMessage()).split("=")

        return float(x), float(y), float(z), float(u), float(v), float(w)

    @checkForRun
    async def getLowLimits(self):
        """
        get current low positions limits
        """
        await self.communicator.sendMessage(self.hexc.getLowPositionSoftLimit())
        axis1, x = str(await self.communicator.getMessage()).split("=")
        axis2, y = str(await self.communicator.getMessage()).split("=")
        axis3, z = str(await self.communicator.getMessage()).split("=")
        axis4, u = str(await self.communicator.getMessage()).split("=")
        axis5, v = str(await self.communicator.getMessage()).split("=")
        axis6, w = str(await self.communicator.getMessage()).split("=")

        return float(x), float(y), float(z), float(u), float(v), float(w)

    @checkForRun
    async def getHighLimits(self):
        """
        Update current high positions limits
        """
        await self.communicator.sendMessage(self.hexc.getHighPositionSoftLimit())
        axis1, x = str(await self.communicator.getMessage()).split("=")
        axis2, y = str(await self.communicator.getMessage()).split("=")
        axis3, z = str(await self.communicator.getMessage()).split("=")
        axis4, u = str(await self.communicator.getMessage()).split("=")
        axis5, v = str(await self.communicator.getMessage()).split("=")
        axis6, w = str(await self.communicator.getMessage()).split("=")

        return float(x), float(y), float(z), float(u), float(v), float(w)

    @checkForRun
    async def getSystemVelocity(self):
        """
        get current system velocity
        """
        await self.communicator.sendMessage(self.hexc.getSystemVelocity())
        systemVelocity = float(await self.communicator.getMessage())
        return systemVelocity

    @checkForRun
    async def getOnTargetState(self):
        """
        Returns true if it is on Target
        """
        await self.communicator.sendMessage(self.hexc.getOnTargetState())
        Axis1, onTargetX = str(await self.communicator.getMessage()).split("=")
        Axis2, onTargetY = str(await self.communicator.getMessage()).split("=")
        Axis3, onTargetZ = str(await self.communicator.getMessage()).split("=")
        Axis4, onTargetU = str(await self.communicator.getMessage()).split("=")
        Axis5, onTargetV = str(await self.communicator.getMessage()).split("=")
        Axis6, onTargetW = str(await self.communicator.getMessage()).split("=")
        return (bool(int(onTargetX)), bool(int(onTargetY)), bool(int(onTargetZ)),
                bool(int(onTargetU)), bool(int(onTargetV)), bool(int(onTargetW)))

    @checkForRun
    async def getMotionStatus(self):
        """
        Returns motion status in order X, Y, Z, U, V, W, A, B
        where True means it's moving and False for not moving
        """
        await self.communicator.sendMessage(self.hexc.requestMotionStatus())
        message = await self.communicator.getMessage()
        print("Message " + message)
        result = int(message, 16)
        status = '{0:08b}'.format(result)

        return (bool(int(status[7])), bool(int(status[6])), bool(int(status[5])), bool(int(status[4])),
                bool(int(status[3])), bool(int(status[2])), bool(int(status[1])), bool(int(status[0])))

    @checkForRun
    async def getPositionChangeStatus(self):
        """
        Returns position change status for X, Y, Z, U, V, W, A, B
        where True means it's position has changed since last query
        """
        await self.communicator.sendMessage(self.hexc.queryForPositionChange())
        result = int(await self.communicator.getMessage())
        status = '{0:08b}'.format(result)
        return (bool(status[7]), bool(status[6]), bool(status[5]), bool(status[4]),
                bool(status[3]), bool(status[2]), bool(status[1]), bool(status[0]))

    @checkForRun
    async def getReadyStatus(self):
        """
        Check if the hardware is ready to get commands, and update
        current class variable  'self.controllerReady' accordingly
        """
        await self.communicator.sendMessage(self.hexc.requestControllerReadyStatus())
        response = await self.communicator.getMessage()
        ready = response == "±"
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
        return self.maxPositionX, self.maxPositionY, self.maxPositionZ, \
            self.maxPositionU, self.maxPositionV, self.maxPositionW, \
            self.minPositionX, self.minPositionY, self.minPositionZ, \
            self.minPositionU, self.minPositionV, self.minPositionW

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
        return self.positionX, self.positionY, self.positionZ, \
            self.positionU, self.positionV, self.positionW

    def getPivot(self):
        return self.pivotX, self.pivotY, self.pivotZ

    def getSystemVelocity(self):
        return self.systemVelocity
