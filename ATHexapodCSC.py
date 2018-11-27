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

from lsst.ts.salobj import *
import asyncio
import contextlib
import os
import random
import socket
import string
import time
import warnings

import numpy as np

try:
    import SALPY_ATHexapod
except ImportError:
    warnings.warn("Could not import SALPY_ATHexapod; ATHexapodCsc will not work")

import ATHexapodSim

class configATHexapod:
    telemetryInterval = 0.5
    
    class posLimits:
        xyMax = 0.0
        zMin = 0.0
        zMax = 0.0
        uvMax = 0.0
        wMin = 0.0
        wMax = 0.0
    class speedLimits:
        xyMax = 0.1
        rxryMax = 0.0
        zMax = 0.0
        rzMax = 0.0

class stateATHexapod:
    time = 0.0
    xpos = 0.0
    ypos = 0.0
    zpos = 0.0
    uvec = 0.0
    vvec = 0.0
    wvec = 0.0
    xoff = 0.0
    yoff = 0.0
    zoff = 0.0
    uoff = 0.0
    voff = 0.0
    woff = 0.0
    xpivot = 0.0
    ypivot = 0.0
    zpivot = 0.0

class cmdATHexapod:
    time = 0.0
    xpos = 0.0
    ypos = 0.0
    zpos = 0.0
    uvec = 0.0
    vvec = 0.0
    wvec = 0.0
    xoff = 0.0
    yoff = 0.0
    zoff = 0.0
    uoff = 0.0
    voff = 0.0
    woff = 0.0
    xpivot = 0.0
    ypivot = 0.0
    zpivot = 0.0

class simATHexapod:
    hdwDelayApplyPositionLimits = 10  # seconds
    hdwDelayMoveToPosition = 5  # seconds
    hdwDelayApplySpeedLimits = 1
    hdwProbFailure = 0.1
    moveEpsilon = 0.01  # how close to get to target
    positionLoopDeltaT = 0.1

class ATHexapodCsc(base_csc.BaseCsc):
    """A skeleton implementation of ATHexapod
    Supported commands:

    * (import from ATHexpodSummary.txt)
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
    def __init__(self, index, initial_state=base_csc.State.STANDBY):
        if initial_state not in base_csc.State:
            raise ValueError(f"intial_state={initial_state} is not a salobj.State enum")
        super().__init__(SALPY_ATHexapod, index)
        self.summary_state = initial_state
        self.conf = configATHexapod()
        self.simSettings = simATHexapod()
        self.simState = stateATHexapod()
        self.cmdState = cmdATHexapod()
        self.sim = ATHexapodSim.simATHexapod(self.simSettings, self.conf, self.simState)

        self.telTask = None
        #
        # set up event data structures
        #
        self.evt_settingsAppliedPositions_data = self.evt_settingsAppliedPositions.DataType()

        # set up telemetry data structures

        self.tel_actuatorPositions_data = self.tel_actuatorPositions.DataType()

        #
        print('summary state: ', self.summary_state)
        #
        # start the telemetry loop as a task. It won't actually send telemetry
        # unless the CSC is in the STANDBY or ENABLED states

        print('starting telemetryLoop')
        asyncio.ensure_future(self.telemetryLoop())

    def end_standby(self):
        if self.telTask and not self.telTask.done():
            self.telTask.cancel()
        super().end_standby()
    
    async def telemetryLoop(self):
        if self.telTask and not self.telTask.done():
            self.telTask.cancel()
        
        while self.summary_state in (base_csc.State.STANDBY, base_csc.State.ENABLED):
            self.telTask = await asyncio.sleep(self.conf.telemetryInterval)
            self.sendTelemetry()

    def sendTelemetry(self):
        print('sendTelemetry: ', '{:.4f}'.format(time.time()))
        # stuff some fake data into self.tel_actuatorPositions_data before doing the put
        # these will come from stateATHexapod
        self.tel_actuatorPositions_data.raw[0] = self.simState.xpos
        print('telemetry xpos:', self.simState.xpos)
        self.tel_actuatorPositions.put(self.tel_actuatorPositions_data)
        
    async def do_applyPositionLimits(self, id_data):


        self.assert_enabled("applyPositionLimits")
        setattr(self.conf.posLimits, 'xyMax', getattr(id_data.data, 'xyMax'))
        setattr(self.conf.posLimits, 'zMin', getattr(id_data.data, 'zMin'))
        setattr(self.conf.posLimits, 'zMax', getattr(id_data.data, 'zMax'))
        setattr(self.conf.posLimits, 'uvMax', getattr(id_data.data, 'uvMax'))
        setattr(self.conf.posLimits, 'wMin', getattr(id_data.data, 'wMin'))
        setattr(self.conf.posLimits, 'wMax', getattr(id_data.data, 'wMax'))


        # And here is where to put in some mock behavior for the hardware, or later,
        # code that connects to the actual hardware

        await asyncio.sleep(self.simSettings.hdwDelayApplyPositionLimits)
        
        # copy from posLimits into self.evt_settingsAppliedPositions_data
        # (and what do we do with the other elements of that data structure?
        # just leave them with whatever value they have, I guess

        # should I use getattr here instead of the more direct .xyMax?
        setattr(self.evt_settingsAppliedPositions_data, 'limitXYMax', self.conf.posLimits.xyMax)
        setattr(self.evt_settingsAppliedPositions_data, 'limitZMin', self.conf.posLimits.zMin)
        setattr(self.evt_settingsAppliedPositions_data, 'limitZMax', self.conf.posLimits.zMax)
        setattr(self.evt_settingsAppliedPositions_data, 'limitUVMax', self.conf.posLimits.uvMax)
        setattr(self.evt_settingsAppliedPositions_data, 'limitWMin', self.conf.posLimits.wMin)
        setattr(self.evt_settingsAppliedPositions_data, 'limitWMax', self.conf.posLimits.wMax)

        # send the event
        self.evt_settingsAppliedPositions.put(self.evt_settingsAppliedPositions_data)
        
    
    async def do_moveToPosition(self, id_data):

        self.assert_enabled("moveToPosition")
        setattr(self.cmdState, 'xpos', getattr(id_data.data, 'x'))
        setattr(self.cmdState, 'ypos', getattr(id_data.data, 'y'))
        setattr(self.cmdState, 'zpos', getattr(id_data.data, 'z'))
        setattr(self.cmdState, 'uvec', getattr(id_data.data, 'u'))
        setattr(self.cmdState, 'vvec', getattr(id_data.data, 'v'))
        setattr(self.cmdState, 'wvec', getattr(id_data.data, 'w'))

        # And here is where to put in some mock behavior for the hardware, or later,
        # code that connects to the actual hardware

        await self.sim.simMoveToPosition(self.cmdState)

        setattr(self.evt_settingsAppliedPositions_data, 'positionX', self.cmdState.xpos)
        setattr(self.evt_settingsAppliedPositions_data, 'positionY', self.cmdState.ypos)
        setattr(self.evt_settingsAppliedPositions_data, 'positionZ', self.cmdState.zpos)
        setattr(self.evt_settingsAppliedPositions_data, 'positionU', self.cmdState.uvec)
        setattr(self.evt_settingsAppliedPositions_data, 'positionV', self.cmdState.vvec)
        setattr(self.evt_settingsAppliedPositions_data, 'positionW', self.cmdState.wvec)

        # send the event
        self.evt_settingsAppliedPositions.put(self.evt_settingsAppliedPositions_data)


    def do_setMaxSpeeds(self, id_data):
        self.assert_enabled("setMaxSpeeds")

        setattr(self.conf.speedLimits, 'xyMax', getattr(id_data.data, 'xyMax'))
        setattr(self.conf.speedLimits, 'rxryMax', getattr(id_data.data, 'rxryMax'))
        setattr(self.conf.speedLimits, 'zMax', getattr(id_data.data, 'zMax'))
        setattr(self.conf.speedLimits, 'rzMax', getattr(id_data.data, 'rzMax'))

#        await asyncio.sleep(self.simSettings.hdwDelayApplySpeedLimits)

        setattr(self.evt_settingsAppliedPositions_data, 'velocityXYMax', self.conf.speedLimits.xyMax)
        setattr(self.evt_settingsAppliedPositions_data, 'velocityRxRyMax', self.conf.speedLimits.rxryMax)
        setattr(self.evt_settingsAppliedPositions_data, 'velocityZMax', self.conf.speedLimits.zMax)
        setattr(self.evt_settingsAppliedPositions_data, 'velocityRzMax', self.conf.speedLimits.rzMax)

        # send the event
        self.evt_settingsAppliedPositions.put(self.evt_settingsAppliedPositions_data)

    
    def do_applyPositionOffset(self, id_data):
        self.assert_enabled("applyPositionOffset")
        pass
    
    def do_stopAllAxes(self, id_data):
        self.assert_enabled("stopAllAxes")
        pass
    
    def do_pivot(self, id_data):
        self.assert_enabled("pivot")
        pass
    
