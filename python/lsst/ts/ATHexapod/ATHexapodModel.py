__all__ = ["Model"]

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
    inMotion = False


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


class salCommandGeneric(object):
    pass


class Model:
    def __init__(self):
        self.detailedState = HexapodDetailedStates.NOTINMOTIONSTATE
        self.configuration = ConfigurationKeeper()
        self.realPosition = StateATHexapodPosition()
        self.targetPosition = CmdATHexapodPosition()
        self.targetPivot = CmdATHexapodPivot()
        self.initialSetup = None
        self.hexController = ATHexapodController()

    def updateSettings(self, settingsToApply):
        """Update settings according to settingsToApply

        Arguments:
            settingsToApply {String} -- SettingsToApply from start command that defines
            what set of settings to use.
        """

        self.configuration.updateConfiguration(settingsToApply)

    async def aplplyReference(self):
        """ Apply reference If any of the axes is not referenced
        """
        refx, refy, refz, refu, refv, refw, refa, refb = await self.hexController.getReferenceStatus()
        if(not (refx or refy or refz or refu or refv or refw or refa or refb)):
            await self.hexController.initializePosition()

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
        self.realPosition = StateATHexapodPosition()
        self.targetPosition = CmdATHexapodPosition()
        self.detailedState = HexapodDetailedStates.NOTINMOTIONSTATE

        await self.aplplyReference()

        await self.waitUntilReadyForCommand()
        self.initialSetup = self.configuration.getInitialHexapodSetup()
        # Apply position limits to hardware from configuration files
        command = salCommandGeneric()
        command.xyMax = self.initialSetup.limitXYMax
        command.zMin = self.initialSetup.limitZMin
        command.zMax = self.initialSetup.limitZMax
        command.uvMax = self.initialSetup.limitUVMax
        command.wMin = self.initialSetup.limitWMin
        command.wMax = self.initialSetup.limitWMax
        await self.applyPositionLimits(command, skipState=True)

        # Apply pivots to hardware from configuration files
        # command = salCommandGeneric()
        # command.x = self.initialSetup.pivotX
        # command.y = self.initialSetup.pivotY
        # command.z = self.initialSetup.pivotZ
        # await self.pivot(command, skipState=True)
        command = salCommandGeneric()
        command.speed = self.initialSetup.speed
        await self.setMaxSystemSpeeds(command, skipState=True)

    async def disconnect(self):
        """Safely shutdown the ATHexapod
        """

        await self.hexController.disconnect()

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
        # Check if hexapod is in motion (Not working with simulator, test with real hardware later...)
        # Xm, Ym, Zm, Um, Vm, Wm, Am, Bm = await self.hexController.getMotionStatus()
        # inMotion = (Xm or Ym or Zm or Um or Vm or Wm or Am or Bm)
        # print(f"In motion {Xm}  {Ym}  {Zm}  {Um}  {Vm}  {Wm}  {Am}  {Bm} ")
        # Get positions and update
        X, Y, Z, U, V, W = await self.hexController.getRealPositions()
        Xp, Yp, Zp = await self.hexController.getPivot()
        self.updatePosition(X=X, Y=Y, Z=Z, U=U, V=V, W=W, Xp=Xp, Yp=Yp, Zp=Zp)
        self.detailedState = HexapodDetailedStates.INMOTIONSTATE if self.realPosition.inMotion \
            else HexapodDetailedStates.NOTINMOTIONSTATE
        return self.realPosition.inMotion

    async def moveToPosition(self, salCommand):
        """Send command to move to the Hexapod controller.

        Arguments:
            salCommand {cmd_moveToPosition_data} -- Position commanded
        """
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        X = salCommand.x
        Y = salCommand.y
        Z = salCommand.z
        U = salCommand.u
        V = salCommand.v
        W = salCommand.w
        # Check in hardware if position is valid
        await self.assertValidPosition(salCommand)
        # Check if target is out of limits
        self.assertPositionLimits(X=X, Y=Y, Z=Z, U=U, V=V, W=W)
        # Send command to move to the controller
        await self.hexController.moveToPosition(X=X, Y=Y, Z=Z, U=U, V=V, W=W)
        self.realPosition.inMotion = True
        self.detailedState = HexapodDetailedStates.INMOTIONSTATE
        # Update target
        Xc, Yc, Zc, Uc, Vc, Wc = await self.hexController.getTargetPositions()
        self.updateCommandedPosition(X=Xc, Y=Yc, Z=Zc, U=Uc, V=Vc, W=Wc)

    async def applyPositionLimits(self, salCommand, skipState=False):
        """Send command to set position limits to the Hexapod controller.

        Arguments:
            salCommand {cmd_applyPositionLimits_data} -- Position limits set
        """
        if(not skipState):
            self.assertInMotion(inspect.currentframe().f_code.co_name)

        # Implement limits in hardware and software
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
        self.initialSetup.limitXYMax = salCommand.xyMax
        self.initialSetup.limitZMin = salCommand.zMin
        self.initialSetup.limitZMax = salCommand.zMax
        self.initialSetup.limitUVMax = salCommand.uvMax
        self.initialSetup.limitWMin = salCommand.wMin
        self.initialSetup.limitWMax = salCommand.wMax

    async def setMaxSystemSpeeds(self, salCommand, skipState=False):
        """Set maximum speeds, won't be implemented for first version

        Arguments:
            salCommand {cmd_setMaxSpeeds_data} -- Maximum speeds to define in the controller

        Raises:
            ValueError -- Error occurs
        """
        if(not skipState):
            self.assertInMotion(inspect.currentframe().f_code.co_name)
        await self.hexController.setSystemVelocity(salCommand.speed)
        self.initialSetup.speed = await self.hexController.getSystemVelocity()

    async def applyPositionOffset(self, salCommand):
        """Send command to move to an offset to the Hexapod controller.

        Arguments:
            salCommand {cmd_applyPositionOffset_data} -- Position offset commanded
        """
        self.assertInMotion(inspect.currentframe().f_code.co_name)
        positionToCheck = StateATHexapodPosition()
        positionToCheck.x = getattr(self.targetPosition, 'xpos') + salCommand.x
        positionToCheck.y = getattr(self.targetPosition, 'ypos') + salCommand.y
        positionToCheck.z = getattr(self.targetPosition, 'zpos') + salCommand.z
        positionToCheck.u = getattr(self.targetPosition, 'uvec') + salCommand.u
        positionToCheck.v = getattr(self.targetPosition, 'vvec') + salCommand.v
        positionToCheck.w = getattr(self.targetPosition, 'wvec') + salCommand.w
        # Check in hardware if the target is possible
        await self.assertValidPosition(positionToCheck)

        # Check if target is out of limits
        self.assertPositionLimits(X=positionToCheck.x, Y=positionToCheck.y,
                                  Z=positionToCheck.z, U=positionToCheck.u,
                                  V=positionToCheck.v, W=positionToCheck.w)
        # Do move
        await self.hexController.moveOffset(dX=salCommand.x, dY=salCommand.y, dZ=salCommand.z,
                                            dU=salCommand.u, dV=salCommand.v, dW=salCommand.w)
        self.realPosition.inMotion = True
        self.detailedState = HexapodDetailedStates.INMOTIONSTATE
        # Update target
        Xc, Yc, Zc, Uc, Vc, Wc = await self.hexController.getTargetPositions()
        self.updateCommandedPosition(X=Xc, Y=Yc, Z=Zc, U=Uc, V=Vc, W=Wc)

    async def stopAllAxes(self, salCommand):
        """Sends stop all motion to the PI hexapod controller

        Arguments:
            salCommand {cmd_stopAllAxes_data} -- Stop command payload
        """
        self.assertNotInMotion(inspect.currentframe().f_code.co_name)
        await self.hexController.stopMotion()

    async def pivot(self, salCommand, skipState=False):
        """Set pivot into the PI Hexapod controller. U, V and W need to be 0 if not it will report an error.

        Arguments:
            salCommand {cmd_pivot_data} -- Pivot command payload. It has x, y and z

        Raises:
            ValueError -- Command payload not all 0 for u, v, w
            ValueError -- Pivot in the PI Hexapod controller don't match with command
        """
        if(not skipState):
            self.assertInMotion(inspect.currentframe().f_code.co_name)
        threshold = 0.001
        pivotingNotPossible = (abs(self.realPosition.uvec) > threshold) \
            or (abs(self.realPosition.vvec) > threshold) \
            or (abs(self.realPosition.wvec) > threshold)
        if pivotingNotPossible:
            raise ValueError(
                f"To do a pivot all u, v, w need to be 0, currently u={self.realPosition.uvec}, \
                v={self.realPosition.vvec}, w={self.realPosition.wvec}...")
        # Check if pivot target is out of limits
        self.assertPositionLimits(X=salCommand.x, Y=salCommand.y, Z=salCommand.z)
        await self.hexController.setPivot(X=salCommand.x, Y=salCommand.y, Z=salCommand.z)
        self.updateCommandedPosition(Xp=salCommand.x, Yp=salCommand.y, Zp=salCommand.z)
        xp, yp, zp = await self.hexController.getPivot()
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

    def assertNotInMotion(self, commandName):
        """Check if it is in INMOTIONSATE and raise an error when it is not in motion

        Arguments:
            commandName {String} -- Command name to add as information in the error

        Raises:
            ValueError -- Error log to announce that the command is not valid in current state
        """

        if(self.detailedState != HexapodDetailedStates.INMOTIONSTATE):
            raise ValueError(f"{commandName} not allowed in state {self.detailedState.name!r}")

    def assertPositionLimits(self, X=None, Y=None, Z=None, U=None, V=None, W=None):
        """Check if position is out of range and raise an error

        Keyword Arguments:
            X {double} -- Targeted position for X (default: {None})
            Y {double} -- Targeted position for Y (default: {None})
            Z {double} -- Targeted position for Z (default: {None})
            U {double} -- Targeted position for U (default: {None})
            V {double} -- Targeted position for V (default: {None})
            W {double} -- Targeted position for W (default: {None})

        Raises:
            ValueError -- Error if any of the target position axes is out of range
        """
        if (X is not None) and ((X < -self.initialSetup.limitXYMax) or (X > self.initialSetup.limitXYMax)):
            raise ValueError(f"Targe X: {X} is out of range, limits are {-self.initialSetup.limitXYMax} \
                <= X <= {self.initialSetup.limitXYMax}")
        if (Y is not None) and ((Y < -self.initialSetup.limitXYMax) or (Y > self.initialSetup.limitXYMax)):
            raise ValueError(f"Targe Y: {Y} is out of range, limits are {-self.initialSetup.limitXYMax}  \
                <= Y <= {self.initialSetup.limitXYMax}")
        if (Z is not None) and ((Z < self.initialSetup.limitZMin) or (Z > self.initialSetup.limitZMax)):
            raise ValueError(f"Targe Z: {Z} is out of range, limits are {self.initialSetup.limitZMin}  \
                <= Z <= {self.initialSetup.limitZMax}")
        if (U is not None) and ((U < -self.initialSetup.limitUVMax) or (U > self.initialSetup.limitUVMax)):
            raise ValueError(f"Target U: {U} is out of range, limits are {-self.initialSetup.limitUVMax} \
                <= U <= {self.initialSetup.limitUVMax}")
        if (V is not None) and ((V < -self.initialSetup.limitUVMax) or (V > self.initialSetup.limitUVMax)):
            raise ValueError(f"Target V: {V} is out of range, limits are {-self.initialSetup.limitUVMax} \
                <= V <= {self.initialSetup.limitUVMax}")
        if (W is not None) and ((W < self.initialSetup.limitWMin) or (W > self.initialSetup.limitWMax)):
            raise ValueError(f"Target W: {W} is out of range, limits are {-self.initialSetup.limitWMin} \
                <= W <= {self.initialSetup.limitWMax}")

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
        inMotion = False
        threshold = 0.001
        # print(f"X={X} Y={Y} Z={Z} U={U} V={V} W={W}")
        if X is not None:
            if abs(self.realPosition.xpos - X) > threshold:
                inMotion = True
            setattr(self.realPosition, 'xpos', X)
        if Y is not None:
            if abs(self.realPosition.ypos - Y) > threshold:
                inMotion = True
            setattr(self.realPosition, 'ypos', Y)
        if Z is not None:
            if abs(self.realPosition.zpos - Z) > threshold:
                inMotion = True
            setattr(self.realPosition, 'zpos', Z)
        if U is not None:
            if abs(self.realPosition.uvec - U) > threshold:
                inMotion = True
            setattr(self.realPosition, 'uvec', U)
        if V is not None:
            if abs(self.realPosition.vvec - V) > threshold:
                inMotion = True
            setattr(self.realPosition, 'vvec', V)
        if W is not None:
            if abs(self.realPosition.wvec - W) > threshold:
                inMotion = True
            setattr(self.realPosition, 'wvec', W)
        if Xp is not None:
            setattr(self.realPosition, 'xpivot', Xp)
        if Yp is not None:
            setattr(self.realPosition, 'ypivot', Yp)
        if Zp is not None:
            setattr(self.realPosition, 'zpivot', Zp)

        if ((X is not None) or (Y is not None) or (Z is not None) or
           (U is not None) or (V is not None) or (W is not None)):
            self.realPosition.inMotion = inMotion

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

        if X is not None:
            setattr(self.targetPosition, 'xpos', X)
        if Y is not None:
            setattr(self.targetPosition, 'ypos', Y)
        if Z is not None:
            setattr(self.targetPosition, 'zpos', Z)
        if U is not None:
            setattr(self.targetPosition, 'uvec', U)
        if V is not None:
            setattr(self.targetPosition, 'vvec', V)
        if W is not None:
            setattr(self.targetPosition, 'wvec', W)
        if Xp is not None:
            setattr(self.targetPivot, 'xpivot', Xp)
        if Yp is not None:
            setattr(self.targetPivot, 'ypivot', Yp)
        if Zp is not None:
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
        return self.realPosition

    def getTargetPosition(self):
        """Return last target positition

        Returns:
            [CmdATHexapodPosition] -- Last position commanded from moveToPosition or offset commands
        """

        return self.targetPosition

    def getTargetPivot(self):
        """Return last target pivot position

        Returns:
            [CmdATHexapodPivot] -- Last pivot commanded from pivot command
        """

        return self.targetPivot

    async def getRealPivot(self):
        """Return pivot position from the hardware

        Returns:
            [CmdATHexapodPivot] -- Pivot read from the hardware
        """
        pivot = CmdATHexapodPivot
        pivot.x, pivot.y, pivot.z = await self.hexController.getPivot()
        return pivot

    async def getRealPositionLimits(self):
        """Return position limits from the hardware

        Returns:
            [CmdATHexapodPivot] -- Pivot read from the hardware
        """
        command = salCommandGeneric()
        command.xyMax, x, command.zMax, command.uvMax, x, command.wMax = \
            await self.hexController.getHighLimits()
        x, x, command.zMin, x, x, command.wMin = await self.hexController.getLowLimits()
        return command

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
        err = 0.0001
        while (time.time() - initial_time < timeout):
            await asyncio.sleep(loopDelay)
            if self.detailedState is HexapodDetailedStates.NOTINMOTIONSTATE:
                break
        inPosition = (abs(self.realPosition.xpos - self.targetPosition.xpos) < err) and \
                     (abs(self.realPosition.ypos - self.targetPosition.ypos) < err) and \
                     (abs(self.realPosition.zpos - self.targetPosition.zpos) < err) and \
                     (abs(self.realPosition.uvec - self.targetPosition.uvec) < err) and \
                     (abs(self.realPosition.vvec - self.targetPosition.vvec) < err) and \
                     (abs(self.realPosition.wvec - self.targetPosition.wvec) < err)

        await self.waitUntilReadyForCommand()
        if (not inPosition):
            raise ValueError("Position never reached...")

    async def waitUntilReadyForCommand(self, timeout=200):
        """Will request PI Hexapod status, and wait until is ready to receive new commands.
        It will trigger an exception if timeout happens

        Keyword Arguments:
            timeout {int} -- [Seconds until consider a timeout] (default: {200})

        Raises:
            ValueError: Timeout
        """
        initial_time = time.time()
        ready = False
        loopDelay = 0.3
        while (time.time() - initial_time <= timeout):
            await asyncio.sleep(loopDelay)
            ready = await self.hexController.getReadyStatus()
            if ready:
                break
        if (not ready):
            raise ValueError("PI Contoller timeout: System never ready")

    async def waitUntilStop(self):
        initial_time = time.time()
        timeout = 600
        loopDelay = 0.3
        while (time.time() - initial_time <= timeout):
            await asyncio.sleep(loopDelay)
            if self.detailedState is HexapodDetailedStates.NOTINMOTIONSTATE:
                break
        await self.waitUntilReadyForCommand()
        if (time.time() - initial_time >= timeout):
            raise ValueError("Motion never stopped...")

    def getTcpConfiguration(self):
        """Return TCP configuration

        Returns:
            [TcpConfiguration] -- TCP Configuration read from the configuration file
        """
        tcpConfiguration = self.configuration.getTcpConfiguration()
        return tcpConfiguration

    async def getMaxSystemSpeeds(self):
        """Return System Velocity from the PI controller

        Returns:
            [float] -- Maximum velocity in mm/s
        """

        self.initialSetup.speed = await self.hexController.getSystemVelocity()
        return self.initialSetup.speed


class HexapodDetailedStates(Enum):
    INMOTIONSTATE = SALPY_ATHexapod.ATHexapod_shared_DetailedState_InMotionState
    NOTINMOTIONSTATE = SALPY_ATHexapod.ATHexapod_shared_DetailedState_NotInMotionState


class HexapodErrorCodes(Enum):
    DEVICENOTFOUND = 8261
