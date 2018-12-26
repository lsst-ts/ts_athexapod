__all__ = ["Model", "HexapodDetailedStates"]

from enum import Enum
import SALPY_ATHexapod
import inspect
from lsst.ts.ATHexapod.ATHexapodConfiguration import ConfigurationKeeper
from lsst.ts.ATHexapod.ATHexapodController import ATHexapodController
import asyncio


class StateATHexapodPosition:
    time = 0.0
    xpos = 0.0
    ypos = 0.0
    zpos = 0.0
    uvec = 0.0
    vvec = 0.0
    wvec = 0.0
    xpivot = 0.0
    ypivot = 0.0
    zpivot = 0.0


class CmdATHexapodPosition:
    time = 0.0
    xpos = 0.0
    ypos = 0.0
    zpos = 0.0
    uvec = 0.0
    vvec = 0.0
    wvec = 0.0


class CmdATHexapodPivot:
    xpivot = 0.0
    ypivot = 0.0
    zpivot = 0.0


class Model:
    def __init__(self):
        self.detailedState = HexapodDetailedStates.NOTINMOTIONSTATE
        self.configuration = ConfigurationKeeper()
        self.realPosition = StateATHexapodPosition()
        self.targetPosition = CmdATHexapodPosition()
        self.targetPivot = CmdATHexapodPivot()
        self.hexController = ATHexapodController()

    def updateSettings(self, settingsToApply):
        self.configuration.updateConfiguration(settingsToApply)

    async def initialize(self):
        tcpConfiguration = self.configuration.getTcpConfiguration()

        endStr = '\n' if tcpConfiguration.endStr is "endl" else '\n'
        self.hexController.configureCommunicator(address=tcpConfiguration.host, port=tcpConfiguration.port,
                                                 connectTimeout=tcpConfiguration.connectionTimeout,
                                                 readTimeout=tcpConfiguration.readTimeout,
                                                 sendTimeout=tcpConfiguration.sendTimeout,
                                                 endStr=endStr, maxLength=tcpConfiguration.maxLength)
        await self.hexController.connect()
        await self.hexController.initializePosition()

    def isInMotion(self):
        """Check if ATHexapod is in motion and return True if it is in motion
        Returns:
            bool -- True if it is in motion, false if not
        """
        return self.detailedState is HexapodDetailedStates.INMOTIONSTATE

    async def updateState(self):
        """Check if the Hexapod is in motion and update positions and detailed state.

        Returns:
            inMotion -- True if any of the axes is in motion
        """
        # Check if hexapod is in motion
        Xm, Ym, Zm, Um, Vm, Wm, Am, Bm = await self.hexController.getMotionStatus()
        inMotion = (Xm or Ym or Zm or Um or Vm or Wm or Am or Bm)
        # Get positions and update
        X, Y, Z, U, V, W = await self.hexController.getRealPositions()
        Xp, Yp, Zp = await self.hexController.getPivot()
        self.updatePosition(X=X, Y=Y, Z=Z, U=U, V=V, W=W, Xp=Xp, Yp=Yp, Zp=Zp)
        self.detailedState = HexapodDetailedStates.INMOTIONSTATE if inMotion \
            else HexapodDetailedStates.NOTINMOTIONSTATE
        return inMotion

    async def moveToPosition(self, salCommand):
        """Send command to move to the Hexapod controller.

        Arguments:
            salCommand {cmd_moveToPosition_data} -- Position commanded
        """
        await self.updateState()
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        X = salCommand.x
        Y = salCommand.y
        Z = salCommand.z
        U = salCommand.u
        V = salCommand.v
        W = salCommand.w
        self.assertValidPosition(self, salCommand)
        await self.hexController.moveToPosition(X=X, Y=Y, Z=Z, U=U, V=V, W=W)
        await self.updateState()

    async def applyPositionLimits(self, salCommand):
        """Send command to set position limits to the Hexapod controller.

        Arguments:
            salCommand {cmd_applyPositionLimits_data} -- Position limits set
        """

        await self.updateState()
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        await self.hexController.setPositionLimits(minPositionX=-salCommand.xyMax,
                                                   minPositionY=-salCommand.xyMax,
                                                   minPositionZ=salCommand.zMin,
                                                   minPositionU=-salCommand.uvMax,
                                                   minPositionV=-salCommand.uvMax,
                                                   minPositionW=salCommand.wMin,
                                                   maxPositionX=salCommand.xyMax,
                                                   maxPositionY=salCommand.xyMax,
                                                   maxPositionZ=salCommand.zMax,
                                                   maxPositionU=salCommand.uvMax,
                                                   maxPositionV=salCommand.uvMax,
                                                   maxPositionW=salCommand.wMax)

    async def setMaxSpeeds(self, salCommand):
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        raise ValueError("Command not implemented...")

    async def applyPositionOffset(self, salCommand):
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        """Send command to move to an offset to the Hexapod controller.

        Arguments:
            salCommand {cmd_applyPositionOffset_data} -- Position offset commanded
        """
        await self.updateState()
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        positionToCheck = StateATHexapodPosition()
        positionToCheck.x = getattr(self.realPosition, 'xpos') + salCommand.x
        positionToCheck.y = getattr(self.realPosition, 'ypos') + salCommand.y
        positionToCheck.z = getattr(self.realPosition, 'zvec') + salCommand.z
        positionToCheck.u = getattr(self.realPosition, 'uvec') + salCommand.u
        positionToCheck.v = getattr(self.realPosition, 'vvec') + salCommand.v
        positionToCheck.w = getattr(self.realPosition, 'wvec') + salCommand.w
        await self.assertValidPosition.validPosition(X=positionToCheck.x, Y=positionToCheck.y,
                                                     Z=positionToCheck.z, U=positionToCheck.u,
                                                     V=positionToCheck.v, W=positionToCheck.w)
        await self.hexController.moveOffset(dX=salCommand.x, dY=salCommand.y, dZ=salCommand.z,
                                            dU=salCommand.u, dV=salCommand.v, dW=salCommand.w)
        await self.updateState()

    async def stopAllAxes(self, salCommand):
        await self.updateState()
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        self.hexController.stopMotion()

    def pivot(self, salCommand):
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        pass

    def assertInMotion(self, commandName):
        if(self.detailedState != HexapodDetailedStates.NOTINMOTIONSTATE):
            raise ValueError(f"{commandName} not allowed in state {self.detailedState.name!r}")

    async def assertValidPosition(self, commandedPosition):
        """Check if position is reachable, if not through an error.
        Arguments:
            commandedPosition {StateATHexapod} -- Position to check if it is reachable
        Raises:
            ValueError -- Raise error if position is not possible
        """
        X = commandedPosition.x
        Y = commandedPosition.y
        Z = commandedPosition.z
        U = commandedPosition.u
        V = commandedPosition.v
        W = commandedPosition.w
        validPosition = await self.hexController.validPosition(X=X, Y=Y, Z=Z, U=U, V=V, W=W)
        if not validPosition:
            raise ValueError(
                f"Position X={X}, Y={Y}, Z={Z}, U={U}, V={V} , W={W} not allowed")

    def updatePosition(self, X: float = None, Y: float = None, Z: float = None, U: float = None,
                       V: float = None, W: float = None, Xp: float = None,
                       Yp: float = None, Zp: float = None):
        if X:
            setattr(self.realPosition, 'xpos', X)
        if Y:
            setattr(self.realPosition, 'ypos', Y)
        if Z:
            setattr(self.realPosition, 'zpos', Z)
        if U:
            setattr(self.realPosition, 'uvec', U)
        if V:
            setattr(self.realPosition, 'vvec', V)
        if W:
            setattr(self.realPosition, 'wvec', W)
        if Xp:
            setattr(self.realPosition, 'xpivot', Xp)
        if Yp:
            setattr(self.realPosition, 'ypivot', Yp)
        if Zp:
            setattr(self.realPosition, 'zpivot', Zp)


class HexapodDetailedStates(Enum):
    INMOTIONSTATE = SALPY_ATHexapod.ATHexapod_shared_DetailedState_InMotionState
    NOTINMOTIONSTATE = SALPY_ATHexapod.ATHexapod_shared_DetailedState_NotInMotionState
