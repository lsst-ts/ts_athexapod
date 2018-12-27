__all__ = ["Model", "HexapodDetailedStates"]

from enum import Enum
import SALPY_ATHexapod
import inspect
from lsst.ts.ATHexapod.ATHexapodConfiguration import ConfigurationKeeper
from lsst.ts.ATHexapod.ATHexapodController import ATHexapodController
import asyncio
import time


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
        """Update settings according to settingsToApply

        Arguments:
            settingsToApply {String} -- SettingsToApply from start command that defines
            what set of settings to use.
        """

        self.configuration.updateConfiguration(settingsToApply)

    async def initialize(self):
        """Initialize and connect to TCP PI Hexapod controller socket
        """

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
        """Set maximum speeds, won't be implemented for first version

        Arguments:
            salCommand {cmd_setMaxSpeeds_data} -- Maximum speeds to define in the controller

        Raises:
            ValueError -- Error occurs
        """

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
        positionToCheck.x = getattr(self.targetPosition, 'xpos') + salCommand.x
        positionToCheck.y = getattr(self.targetPosition, 'ypos') + salCommand.y
        positionToCheck.z = getattr(self.targetPosition, 'zvec') + salCommand.z
        positionToCheck.u = getattr(self.targetPosition, 'uvec') + salCommand.u
        positionToCheck.v = getattr(self.targetPosition, 'vvec') + salCommand.v
        positionToCheck.w = getattr(self.targetPosition, 'wvec') + salCommand.w
        await self.assertValidPosition.validPosition(X=positionToCheck.x, Y=positionToCheck.y,
                                                     Z=positionToCheck.z, U=positionToCheck.u,
                                                     V=positionToCheck.v, W=positionToCheck.w)
        await self.hexController.moveOffset(dX=salCommand.x, dY=salCommand.y, dZ=salCommand.z,
                                            dU=salCommand.u, dV=salCommand.v, dW=salCommand.w)
        self.updateCommandedPosition(X=positionToCheck.x, Y=positionToCheck.y, Z=positionToCheck.z,
                                     U=positionToCheck.u, V=positionToCheck.v, W=positionToCheck.w)
        await self.updateState()

    async def stopAllAxes(self, salCommand):
        """Sends stop all motion to the PI hexapod controller

        Arguments:
            salCommand {cmd_stopAllAxes_data} -- Stop command payload
        """

        await self.updateState()
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        self.hexController.stopMotion()

    async def pivot(self, salCommand):
        """Set pivot into the PI Hexapod controller. U, V and W need to be 0 if not it will report an error.

        Arguments:
            salCommand {cmd_pivot_data} -- Pivot command payload. It has x, y and z

        Raises:
            ValueError -- Command payload not all 0 for u, v, w
            ValueError -- Pivot in the PI Hexapod controller don't match with command
        """

        await self.updateState()
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        threshold = 0.001
        pivotingPossible = (abs(self.realPosition.u) > threshold) \
            or (abs(self.realPosition.v) > threshold) \
            or (abs(self.realPosition.w) > threshold)
        if pivotingPossible:
            raise ValueError(
                f"To do a pivot all u, v, w need to be 0, currently u={self.realPosition.u}, \
                v={self.realPosition.v}, w={self.realPosition.w}...")
        self.hexController.setPivot(X=salCommand.x, Y=salCommand.y, Z=salCommand.z)
        self.updateCommandedPosition(Xp=salCommand.x, Yp=salCommand.y, Zp=salCommand.z)
        xp, yp, zp = self.hexController.getPivot()
        self.updatePosition(Xp=xp, Yp=yp, Zp=zp)
        pivotingNotProperlySet = (abs(xp - salCommand.x) > threshold) or \
            (abs(yp - salCommand.y) > threshold) or \
            (abs(zp - salCommand.z) > threshold)
        if pivotingNotProperlySet:
            raise ValueError(
                f"Pivot not properly set, device pivot x={xp}, y={yp}, z={zp}...")

    def assertInMotion(self, commandName):
        """Check if it is in NOTINMOTIONSATE and raise an error when it is in motion

        Arguments:
            commandName {String} -- Command name to add as information in the error

        Raises:
            ValueError -- Error log to announce that the command is not valid in current state
        """

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
        """Update position in the class

        Keyword Arguments:
            X {float} -- [X position in mm] (default: {None})
            Y {float} -- [Y position in mm] (default: {None})
            Z {float} -- [Z position in mm] (default: {None})
            U {float} -- [U position in degrees] (default: {None})
            V {float} -- [V position in degrees] (default: {None})
            W {float} -- [W position in degrees] (default: {None})
            Xp {float} -- [Y position in mm] (default: {None})
            Yp {float} -- [Y position in mm] (default: {None})
            Zp {float} -- [Y position in mm] (default: {None})
        """

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

    def updateCommandedPosition(self, X: float = None, Y: float = None,
                                Z: float = None, U: float = None,
                                V: float = None, W: float = None, Xp: float = None,
                                Yp: float = None, Zp: float = None):
        """Update commanded position in the class

        Keyword Arguments:
            X {float} -- [X position in mm] (default: {None})
            Y {float} -- [Y position in mm] (default: {None})
            Z {float} -- [Z position in mm] (default: {None})
            U {float} -- [U position in degrees] (default: {None})
            V {float} -- [V position in degrees] (default: {None})
            W {float} -- [W position in degrees] (default: {None})
            Xp {float} -- [Y position in mm] (default: {None})
            Yp {float} -- [Y position in mm] (default: {None})
            Zp {float} -- [Y position in mm] (default: {None})
        """

        if X:
            setattr(self.targetPosition, 'xpos', X)
        if Y:
            setattr(self.targetPosition, 'ypos', Y)
        if Z:
            setattr(self.targetPosition, 'zpos', Z)
        if U:
            setattr(self.targetPosition, 'uvec', U)
        if V:
            setattr(self.targetPosition, 'vvec', V)
        if W:
            setattr(self.targetPosition, 'wvec', W)
        if Xp:
            setattr(self.targetPivot, 'xpivot', Xp)
        if Yp:
            setattr(self.targetPivot, 'ypivot', Yp)
        if Zp:
            setattr(self.targetPivot, 'zpivot', Zp)

    def getTcpConfiguration(self):
        """Return current TCP configuration

        Returns:
            [TcpConfiguration] -- TCP Configuration from the last settingsToApply used
        """

        tcpConfiguration = self.configuration.getTcpConfiguration()
        return tcpConfiguration

    def getInitialHexapodSetup(self):
        """Returns the initialHexapodSetup from the file

        Returns:
            [InitialHexapodSetup] -- initialHexapodSetup from the last settingsToApply used
        """

        initialHexapodSetup = self.configuration.getInitialHexapodSetup()
        return initialHexapodSetup

    async def getRealPosition(self):
        """Return last positition read

        Returns:
            [StateATHexapodPosition] -- Last position read from PI Hexapod controller
        """
        await self.updateState()
        return self.realPosition

    def getTargetPosition(self):
        """Return last target positition

        Returns:
            [CmdATHexapodPosition] -- Last position commanded from moveToPosition or offset commands
        """

        return self.targetPosition

    def getTargetPivot(self):
        """Return last target pivot positition

        Returns:
            [CmdATHexapodPivot] -- Last pivot commanded from pivot command
        """

        return self.targetPivot

    def getSettingVersions(self):
        """Return string with comma separated values as recommended Settings

        Returns:
            [string] -- list of recommended settings
        """

        return self.configuration.getSettingVersions()

    async def waitUntilPosition(self):
        initial_time = time.time()
        timeout = 600
        loopDelay = 0.3
        while (time.time() - initial_time < timeout):
            await self.updateState()
            await asyncio.Sleep(loopDelay)
            if self.detailedState is HexapodDetailedStates.NOTINMOTIONSTATE:
                break
        if (time.time() - initial_time >= timeout):
            raise ValueError("Position never reached...")


class HexapodDetailedStates(Enum):
    INMOTIONSTATE = SALPY_ATHexapod.ATHexapod_shared_DetailedState_InMotionState
    NOTINMOTIONSTATE = SALPY_ATHexapod.ATHexapod_shared_DetailedState_NotInMotionState
