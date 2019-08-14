#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
__all__ = ["ATHexapodCsc"]

from lsst.ts import salobj
from lsst.ts.ATHexapod.ATHexapodModel import Model, HexapodErrorCodes
import asyncio


class ATHexapodCsc(salobj.BaseCsc):
    """A skeleton implementation of ATHexapod
    Supported commands:

    * (import from ATHexapodSummary.txt)
    * The standard state transition commands do the usual thing
      and output the ``summaryState`` event. The ``exitControl``
      command shuts the CSC down.

    Parameters
    ----------
    initial_state : `salobj.State` (optional)
        The initial state of the CSC. Typically one of:
        - State.ENABLED if you want the CSC immediately usable.
        - State.STANDBY if you want full emulation of a CSC.
    """

    def __init__(self, index=0, initial_state=salobj.State.STANDBY, initial_simulation_mode=0):
        if initial_state not in salobj.State:
            raise ValueError(f"intial_state={initial_state} is not a salobj.State enum")
        super().__init__("ATHexapod", index=index, initial_state=initial_state,
                         initial_simulation_mode=initial_simulation_mode)
        self.log.setLevel(10)  # Print all logs
        self.defer_simulation_mode_until_configured = False
        self.summary_state = initial_state
        self.model = Model()
        self.detailedState = 0  # Last deatiled state published. Initialized at 0, which doesn't exist in SAL
        self.appliedSettingsMatchStart = False
        self.telemetryInterval = 1
        self.recoverTimeout = 5  # Times that the CSC try to recover communication before going to Fault state
        self.telTask = None
        #
        # set up event data structures
        #
        self.evt_settingsAppliedPositionLimits_data = self.evt_settingsAppliedPositionLimits.DataType()
        self.evt_settingsAppliedVelocities_data = self.evt_settingsAppliedVelocities.DataType()
        self.evt_settingsAppliedPivot_data = self.evt_settingsAppliedPivot.DataType()
        self.evt_settingsAppliedTcp_data = self.evt_settingsAppliedTcp.DataType()
        self.evt_positionUpdate_data = self.evt_positionUpdate.DataType()
        self.evt_appliedSettingsMatchStart_data = self.evt_appliedSettingsMatchStart.DataType()
        self.evt_detailedState_data = self.evt_detailedState.DataType()
        self.evt_settingVersions_data = self.evt_settingVersions.DataType()
        self.evt_inPosition_data = self.evt_inPosition.DataType()
        self.evt_errorCode_data = self.evt_errorCode.DataType()

        # set up telemetry data structures
        self.tel_positionStatus_data = self.tel_positionStatus.DataType()
        self.log.debug('summary state: ' + str(self.summary_state))

        # Publish list of recommended settings
        settingVersions = self.model.getSettingVersions()
        self.evt_settingVersions_data.recommendedSettingsLabels = settingVersions
        self.evt_settingVersions.put(self.evt_settingVersions_data)

        self.log.debug('starting telemetryLoop')
        asyncio.ensure_future(self.telemetryLoop())

    async def do_start(self, id_data):
        """Start the TCP connection in the ATHexapod

        Arguments:
            id_data {cmd_start} -- Start to with settingsToApply
            attribute

        Raises:
            ValueError: Raise exception if cannont connect or initialize
        """
        if self.summary_state is not salobj.State.STANDBY:
            raise ValueError(f"Start not valid in state: {self.summary_state.name}")
        self.publish_appliedSettingsMatchStart(True)
        self.model.updateSettings(id_data.settingsToApply)
        try:
            self.log.debug("Initializing hexapod position")
            await self.model.initialize()
            self.publishSettingsAppliedTcp()
        except Exception as e:
            await self.model.disconnect()
            raise(e)
        await super().do_start(id_data)

    async def do_enable(self, id_data):
        self.log.debug("Initializing position, please wait....")
        await self.model.applyReference()
        self.log.debug("Applying configuration to the controller....")
        await self.model.configure()
        self.log.debug("Position initialized...")
        await self.publish_currentPivot()  # Not configurable any more.... (for now....)
        await self.publish_positionLimits()
        await self.publish_systemVelocity()
        self.log.debug("Enable CSC")
        await super().do_enable(id_data)

    async def do_standby(self, id_data):
        await self.model.disconnect()
        await super().do_standby(id_data)

    async def end_standby(self, id_data):
        await super().end_standby(id_data)

    async def telemetryLoop(self):
        if self.telTask and not self.telTask.done():
            self.telTask.cancel()
        i = 0
        while True:
            if self.summary_state in (salobj.State.DISABLED, salobj.State.ENABLED):
                try:
                    await self.sendTelemetry()
                    i = 0
                except Exception as err:
                    i = i + 1
                    # if there are more than self.recoverTimeout attempt and is not recovering,
                    # go to Fault state
                    if i >= self.recoverTimeout:
                        self.evt_errorCode_data.errorCode = HexapodErrorCodes.DEVICENOTFOUND.value
                        self.evt_errorCode_data.errorReport = "Device not found in the network"
                        self.evt_errorCode_data.traceback = str(err)
                        self.evt_errorCode.put(self.evt_errorCode_data)
                        await self.model.disconnect()
                        self.fault()
            self.telTask = await asyncio.sleep(self.telemetryInterval)

    async def sendTelemetry(self):
        await self.model.updateState()

        # Get current positions and publish
        target = self.model.getTargetPosition()
        position = await self.model.getRealPosition()

        self.tel_positionStatus_data.setpointPosition[0] = target.xpos
        self.tel_positionStatus_data.setpointPosition[1] = target.ypos
        self.tel_positionStatus_data.setpointPosition[2] = target.zpos
        self.tel_positionStatus_data.setpointPosition[3] = target.uvec
        self.tel_positionStatus_data.setpointPosition[4] = target.vvec
        self.tel_positionStatus_data.setpointPosition[5] = target.wvec

        self.tel_positionStatus_data.reportedPosition[0] = position.xpos
        self.tel_positionStatus_data.reportedPosition[1] = position.ypos
        self.tel_positionStatus_data.reportedPosition[2] = position.zpos
        self.tel_positionStatus_data.reportedPosition[3] = position.uvec
        self.tel_positionStatus_data.reportedPosition[4] = position.vvec
        self.tel_positionStatus_data.reportedPosition[5] = position.wvec

        for i in range(6):
            self.tel_positionStatus_data.positionFollowingError[i] = abs(
                self.tel_positionStatus_data.setpointPosition[i] -
                self.tel_positionStatus_data.reportedPosition[i])

        self.tel_positionStatus.put(self.tel_positionStatus_data)

        self.publishDetailedState(self.model.detailedState.value)

    async def do_applyPositionLimits(self, id_data):
        self.assert_enabled("applyPositionLimits")
        await self.model.applyPositionLimits(id_data.data)
        await self.publish_positionLimits()
        self.publish_appliedSettingsMatchStart(False)

    def do_setLogLevel(self):
        pass

    def do_setSimulationMode(self):
        pass

    async def publish_positionLimits(self):
        data = await self.model.getRealPositionLimits()
        # should I use getattr here instead of the more direct .xyMax?
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitXYMax', data.xyMax)
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitZMin', data.zMin)
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitZMax', data.zMax)
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitUVMax', data.uvMax)
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitWMin', data.wMin)
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitWMax', data.wMax)

        # send the event
        self.evt_settingsAppliedPositionLimits.put(self.evt_settingsAppliedPositionLimits_data)

    async def publish_systemVelocity(self):
        velocity = await self.model.getMaxSystemSpeeds()
        self.evt_settingsAppliedVelocities_data.systemSpeed = velocity
        # send the event
        self.evt_settingsAppliedVelocities.put(self.evt_settingsAppliedVelocities_data)

    async def do_moveToPosition(self, id_data):
        self.assert_enabled("moveToPosition")
        if (self.simulation_mode == 1):
            id_data.x = round(id_data.x, 3)
            id_data.y = round(id_data.y, 3)
            id_data.z = round(id_data.z, 3)
            id_data.u = round(id_data.u, 3)
            id_data.v = round(id_data.v, 3)
            id_data.w = round(id_data.w, 3)
        await self.model.moveToPosition(id_data.data)
        self.publishPositionUpdate()
        await self.waitUntilPosition()

    async def do_setMaxSystemSpeeds(self, id_data):
        self.assert_enabled("setMaxSystemSpeeds")

        # Execute command in hardware
        await self.model.setMaxSystemSpeeds(id_data.data)

        # Update event datatype
        setattr(self.evt_settingsAppliedVelocities_data, 'systemSpeed', self.model.initialSetup.speed)

        # send the event
        self.evt_settingsAppliedVelocities.put(self.evt_settingsAppliedVelocities_data)
        self.publish_appliedSettingsMatchStart(False)

        # there is no event associated with completing this command

    async def do_applyPositionOffset(self, id_data):
        self.assert_enabled("applyPositionOffset")
        if (self.simulation_mode == 1):
            id_data.x = round(id_data.x, 3)
            id_data.y = round(id_data.y, 3)
            id_data.z = round(id_data.z, 3)
            id_data.u = round(id_data.u, 3)
            id_data.v = round(id_data.v, 3)
            id_data.w = round(id_data.w, 3)
        await self.model.applyPositionOffset(id_data.data)
        self.publishPositionUpdate()
        await self.waitUntilPosition()

    async def do_stopAllAxes(self, id_data):
        self.assert_enabled("stopAllAxes")
        await self.model.stopAllAxes(id_data.data)
        await self.model.waitUntilStop()

    async def do_pivot(self, id_data):
        self.assert_enabled("pivot")
        await self.model.pivot(id_data.data)
        self.publish_appliedSettingsMatchStart(False)
        await self.publish_currentPivot()

    async def publish_currentPivot(self):
        """Publish pivot from hardware
        """

        pivot = await self.model.getRealPivot()
        # Update event datatype
        setattr(self.evt_settingsAppliedPivot_data, 'pivotX', pivot.x)
        setattr(self.evt_settingsAppliedPivot_data, 'pivotY', pivot.y)
        setattr(self.evt_settingsAppliedPivot_data, 'pivotZ', pivot.z)
        # send the event
        self.evt_settingsAppliedPivot.put(self.evt_settingsAppliedPivot_data)

    def publish_appliedSettingsMatchStart(self, value):
        """Publish appliedSettingsMatchStart if different than value

        Arguments:
            value {bool} -- Value to update appliedSettingsMatchStart
        """
        if(value == self.appliedSettingsMatchStart):
            pass
        else:
            self.evt_appliedSettingsMatchStart_data.appliedSettingsMatchStartIsTrue = value
            self.evt_appliedSettingsMatchStart.put(self.evt_appliedSettingsMatchStart_data)
            self.appliedSettingsMatchStart = value

    def publishPositionUpdate(self):
        self.evt_positionUpdate_data.positionX = self.model.targetPosition.xpos
        self.evt_positionUpdate_data.positionY = self.model.targetPosition.ypos
        self.evt_positionUpdate_data.positionZ = self.model.targetPosition.zpos
        self.evt_positionUpdate_data.positionU = self.model.targetPosition.uvec
        self.evt_positionUpdate_data.positionV = self.model.targetPosition.vvec
        self.evt_positionUpdate_data.positionW = self.model.targetPosition.wvec

        self.log.debug('evt_positionUpdate_data:')
        for prop in dir(self.evt_positionUpdate_data):
            if not prop.startswith('__'):
                self.log.debug(prop + str(getattr(self.evt_positionUpdate_data, prop)))
        self.evt_positionUpdate.put(self.evt_positionUpdate_data)

    def publishSettingsAppliedTcp(self):
        tcpSettings = self.model.getTcpConfiguration()

        self.evt_settingsAppliedTcp_data.ip = tcpSettings.host
        self.evt_settingsAppliedTcp_data.port = int(tcpSettings.port)
        self.evt_settingsAppliedTcp_data.readTimeout = float(tcpSettings.connectionTimeout)
        self.evt_settingsAppliedTcp_data.writeTimeout = float(tcpSettings.readTimeout)
        self.evt_settingsAppliedTcp_data.connectionTimeout = float(tcpSettings.sendTimeout)
        self.evt_settingsAppliedTcp.put(self.evt_settingsAppliedTcp_data)

    def publishDetailedState(self, detailedState):
        """Publish detailedState when value cahnge

        Arguments:
            value {HexapodDetailedStates} -- Value to update detailedState
        """
        if(detailedState == self.detailedState):
            pass
        else:
            self.evt_detailedState_data.detailedState = detailedState
            self.evt_detailedState.put(self.evt_detailedState_data)
            self.detailedState = detailedState

    def getCurrentTime(self):
        """Get curret time from SAL

        Returns:
            [double] -- Timestamp from SAL
        """

        return self.salinfo.manager.getCurrentTime()

    async def waitUntilPosition(self):
        """After move is executed, wait until position has been reached and publish inPosition
        """

        # set "inPosition" event to say False
        setattr(self.evt_inPosition_data, 'inPosition', False)
        self.evt_inPosition.put(self.evt_inPosition_data)

        # wait until position is reached
        await self.model.waitUntilPosition()

        # set "inPosition" event to say True
        setattr(self.evt_inPosition_data, 'inPosition', True)

        # send the event
        self.evt_inPosition.put(self.evt_inPosition_data)

    @classmethod
    def add_arguments(cls, parser):
        """Add arguments to the argument parser created by `main`.
        Parameters
        ----------
        parser : `argparse.ArgumentParser`
            The argument parser.
        Notes
        -----
        If you override this method then you should almost certainly override
        `add_kwargs_from_args` as well.
        """
        parser.add_argument("-s", "--simulate", action="store_true",
                            help="Run in simuation mode?")

    @classmethod
    def add_kwargs_from_args(cls, args, kwargs):
        """Add constructor keyword arguments based on parsed arguments.
        Parameters
        ----------
        args : `argparse.namespace`
            Parsed command.
        kwargs : `dict`
            Keyword argument dict for the constructor.
            Update this based on ``args``.
            The index argument will already be present if relevant.
        Notes
        -----
        If you override this method then you should almost certainly override
        `add_arguments` as well.
        """
        kwargs["initial_simulation_mode"] = args.simulate

    async def implement_simulation_mode(self, simulation_mode):
        pass
