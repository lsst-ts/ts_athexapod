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
from lsst.ts import ATHexapodModel
import asyncio
import time

import SALPY_ATHexapod


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

    def __init__(self, index, initial_state=salobj.State.STANDBY):
        if initial_state not in salobj.State:
            raise ValueError(f"intial_state={initial_state} is not a salobj.State enum")
        super().__init__(SALPY_ATHexapod, index)
        self.summary_state = initial_state
        self.model = ATHexapodModel.Model()
        self.appliedSettingsMatchStart = False
        self.telemetryInterval = 1

        self.telTask = None
        #
        # set up event data structures
        #
        self.evt_settingsAppliedPositionLimits_data = self.settingsAppliedPositionLimits.DataType()
        self.evt_settingsAppliedVelocities_data = self.evt_settingsAppliedVelocities.DataType()
        self.evt_settingsAppliedPivot_data = self.evt_settingsAppliedPivot.DataType()
        self.evt_settingsAppliedTcp_data = self.evt_settingsAppliedTcp.DataType()
        self.evt_positionUpdate_data = self.evt_positionUpdate.DataType()
        self.evt_appliedSettingsMatchStart_data = self.evt_appliedSettingsMatchStart.DataType()
        self.evt_detailedState_data = self.evt_detailedState.DataType()
        self.evt_settingVersions_data = self.evt_settingVersions.DataType()

        # set up telemetry data structures

        self.tel_positionStatus_data = self.tel_positionStatus.DataType()
        print('summary state: ', self.summary_state)

        # Publish list of recommended settings
        settingVersions = self.Model.getSettingVersions()
        self.evt_settingVersions_data.recommendedSettingsLabels = settingVersions
        self.evt_settingVersions.put(self.evt_settingVersions_data)

        print('starting telemetryLoop')
        asyncio.ensure_future(self.telemetryLoop())

    def do_start(self, id_data):
        super().do_start(id_data)
        self.publish_appliedSettingsMatchStart(True)
        self.Model.updateSettings(id_data.data.settingsToApply)
        self.Model.initialize()

    def end_standby(self, id_data):
        super().end_standby(id_data)

    async def telemetryLoop(self):
        if self.telTask and not self.telTask.done():
            self.telTask.cancel()

        while True:
            if self.summary_state in (salobj.State.DISABLED, salobj.State.ENABLED):
                self.sendTelemetry()
            self.telTask = await asyncio.sleep(self.telemetryInterval)

    async def sendTelemetry(self):
        print('sendTelemetry: ', '{:.4f}'.format(time.time()))
        # Get current positions and publish
        target = self.Model.getTargetPosition()
        position = await self.Model.getRealPosition()

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

    async def do_applyPositionLimits(self, id_data):
        self.assert_enabled("applyPositionLimits")
        await self.Model.applyPositionLimits(id_data.data)

        # should I use getattr here instead of the more direct .xyMax?
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitXYMax', self.id_data.data.xyMax)
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitZMin', self.id_data.data.zMin)
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitZMax', self.id_data.data.zMax)
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitUVMax', self.id_data.data.uvMax)
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitWMin', self.id_data.data.wMin)
        setattr(self.evt_settingsAppliedPositionLimits_data, 'limitWMax', self.id_data.data.wMax)

        # send the event
        self.evt_settingsAppliedPositionLimits.put(self.evt_settingsAppliedPositionLimits_data)
        self.publish_appliedSettingsMatchStart(False)

    async def do_moveToPosition(self, id_data):
        self.assert_enabled("moveToPosition")

        await self.Model.moveToPosition(id_data.data)

        # set "inPosition" event to say False
        setattr(self.evt_inPosition_data, 'inPosition', False)
        self.evt_inPosition.put(self.evt_inPosition_data)

        # wait until position is reached
        self.Model.waitUntilPosition()

        # set "inPosition" event to say True
        setattr(self.evt_inPosition_data, 'inPosition', True)

        # send the event
        self.evt_inPosition.put(self.evt_inPosition_data)

    async def do_setMaxSpeeds(self, id_data):
        self.assert_enabled("setMaxSpeeds")

        self.Model.setMaxSpeeds(id_data.data)

        setattr(self.evt_settingsAppliedVelocities_data, 'velocityXYMax', id_data.data.xyMax)
        setattr(self.evt_settingsAppliedVelocities_data, 'velocityRxRyMax', id_data.data.rxryMax)
        setattr(self.evt_settingsAppliedVelocities_data, 'velocityZMax', id_data.data.zMax)
        setattr(self.evt_settingsAppliedVelocities_data, 'velocityRzMax', id_data.data.rzMax)

        # send the event
        self.evt_settingsAppliedVelocities.put(self.evt_settingsAppliedVelocities_data)
        self.publish_appliedSettingsMatchStart(False)

        # there is no event associated with completing this command

    async def do_applyPositionOffset(self, id_data):
        self.assert_enabled("applyPositionOffset")
        await self.Model.applyPositionOffset(id_data.data)

    async def do_stopAllAxes(self, id_data):
        self.assert_enabled("stopAllAxes")
        self.Model.stopAllAxes(id_data.data)

    async def do_pivot(self, id_data):
        self.assert_enabled("pivot")
        # Still need to implement...
        self.publish_appliedSettingsMatchStart(False)
        pass

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

    def getCurrentTime(self):
        """Get curret time from SAL

        Returns:
            [double] -- Timestamo from SAL
        """

        return self.salinfo.manager.getCurrentTime()
