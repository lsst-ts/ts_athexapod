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

"""
Simple hardware simulator to be used with ATHexapodCSC
"""

import asyncio
import time
import numpy as np

class simATHexapod:

#   hdwDelayApplyPositionLimits = 10  # seconds
#   hdwDelayMoveToPosition = 5  # seconds
#   hdwProbFailure = 0.1

    def __init__(self, simParams, simLimits, simState):
        self.simParams = simParams
        self.simLimits = simLimits
        self.simState = simState

    def simPositionLimits(self, xyMax, zMin, zMax, uvMax, wMin, wMax):
        self.simLimits.posLimits.xyMax = xyMax
    
    def simSpeedLimits(self, xyMax, rxryMax, zMax, rzMax):
        self.simLimits.speedLimits.xyMax = xyMax
     
    async def simMoveToPosition(self, cmd):
        self.xnew = cmd.xpos
        
        # prep parameters for move
        #
        self.simState.time = time.time()
        # calculate velocities
        #
        deltaX = self.xnew - self.simState.xpos        
        self.xvel = self.simLimits.speedLimits.xyMax * np.sign(deltaX)
        #
        await self.positionLoop()

    async def positionLoop(self):

        print('positionLoop: ', self.simState.xpos, self.xnew, self.xvel)
        while np.abs(self.simState.xpos - self.xnew) > self.simParams.moveEpsilon and np.sign(self.xnew - self.simState.xpos) == np.sign(self.xvel):
            self.simState.xpos += self.xvel * self.simParams.positionLoopDeltaT
            self.simState.time = time.time()
            print('positionLoop: ', self.simState.time, self.simState.xpos)
            await asyncio.sleep(self.simParams.positionLoopDeltaT)

            
