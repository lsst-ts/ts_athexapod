"""
This file is part of ts_tests

Developed for the LSST Telescope and Site Systems.
This product includes software developed by the LSST Project
(https://www.lsst.org).
See the COPYRIGHT file at the top-level directory of this distribution
For details of code ownership.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABLITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have recieved a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import os
import pathlib
import unittest

import parameterized
import yaml
from lsst.ts import athexapod, salobj
from lsst.ts.xml.enums import ATHexapod

STD_TIMEOUT = 15
SHORT_TIMEOUT = 5
TEST_CONFIG_DIR = pathlib.Path(__file__).parents[1].joinpath("tests", "data", "config")


class CscTestCase(salobj.BaseCscTestCase, unittest.IsolatedAsyncioTestCase):
    def basic_make_csc(
        self,
        initial_state=salobj.State.STANDBY,
        config_dir=TEST_CONFIG_DIR,
        simulation_mode=1,
        **kwargs,
    ):
        return athexapod.csc.ATHexapodCSC(
            initial_state=initial_state,
            config_dir=config_dir,
            simulation_mode=simulation_mode,
            **kwargs,
        )

    def setUp(self) -> None:
        os.environ["LSST_SITE"] = "test"

    async def test_configuration(self):
        async with self.make_csc(
            initial_state=salobj.State.STANDBY,
            config_dir=TEST_CONFIG_DIR,
            simulation_mode=1,
        ):
            await self.assert_next_summary_state(salobj.State.STANDBY)

            for bad_config_name in ("no_such_file.yaml", "bad_port.yaml"):
                with self.subTest(bad_config_name=bad_config_name):
                    with salobj.assertRaisesAckError():
                        await self.remote.cmd_start.set_start(
                            configurationOverride=bad_config_name, timeout=STD_TIMEOUT
                        )

            await self.remote.cmd_start.set_start(
                configurationOverride="all.yaml", timeout=STD_TIMEOUT
            )

            await self.assert_next_summary_state(state=salobj.State.DISABLED)

            with open(TEST_CONFIG_DIR / "all.yaml") as fp:
                config_all = yaml.safe_load(fp)

            await self.assert_next_sample(
                topic=self.remote.evt_settingsAppliedVelocities,
                systemSpeed=config_all["speed"],
            )
            await self.assert_next_sample(
                topic=self.remote.evt_settingsAppliedPivot,
                pivotX=config_all["pivot_x"],
                pivotY=config_all["pivot_y"],
                pivotZ=config_all["pivot_z"],
            )
            await self.assert_next_sample(
                topic=self.remote.evt_settingsAppliedTcp,
                ip=config_all["host"],
                port=config_all["port"],
            )

    async def test_standard_state_transitions(self):
        async with self.make_csc(initial_state=salobj.State.STANDBY, simulation_mode=1):
            await self.check_standard_state_transitions(
                enabled_commands=[
                    "applyPositionLimits",
                    "moveToPosition",
                    "setMaxSystemSpeeds",
                    "applyPositionOffset",
                    "pivot",
                    "stopAllAxes",
                ]
            )

    async def test_apply_position_limits(self):
        async with self.make_csc(initial_state=salobj.State.ENABLED, simulation_mode=1):
            await self.assert_next_sample(
                topic=self.remote.evt_settingsAppliedPositionLimits
            )
            await self.remote.cmd_applyPositionLimits.set_start(
                timeout=STD_TIMEOUT, xyMax=12, zMin=-6, zMax=8, uvMax=5, wMin=-3, wMax=7
            )
            await self.assert_next_sample(
                topic=self.remote.evt_settingsAppliedPositionLimits,
                limitXYMax=12,
                limitZMin=-6,
                limitZMax=8,
                limitUVMax=5,
                limitWMin=-3,
                limitWMax=7,
            )

    async def test_move_to_position(self):
        async with self.make_csc(initial_state=salobj.State.ENABLED, simulation_mode=1):
            await self.remote.cmd_moveToPosition.set_start(
                timeout=STD_TIMEOUT, x=4, y=6, z=3, u=4, v=3, w=6
            )
            await asyncio.sleep(SHORT_TIMEOUT)
            await self.assert_next_sample(
                topic=self.remote.evt_inPosition, inPosition=False
            )
            await self.assert_next_sample(
                topic=self.remote.evt_inPosition, inPosition=True
            )
            await self.assert_next_sample(
                topic=self.remote.tel_positionStatus,
                flush=True,
                reportedPosition=[4, 6, 3, 4, 3, 6],
                setpointPosition=[4, 6, 3, 4, 3, 6],
            )

    async def test_set_max_system_speeds(self):
        async with self.make_csc(initial_state=salobj.State.ENABLED, simulation_mode=1):
            await self.remote.cmd_setMaxSystemSpeeds.set_start(
                timeout=STD_TIMEOUT, speed=1
            )
            await self.assert_next_sample(
                topic=self.remote.evt_settingsAppliedVelocities, systemSpeed=1
            )

    async def test_apply_position_offset(self):
        async with self.make_csc(initial_state=salobj.State.ENABLED, simulation_mode=1):
            await self.assert_next_sample(topic=self.remote.evt_positionUpdate)
            position = await self.assert_next_sample(
                topic=self.remote.tel_positionStatus
            )
            await self.remote.cmd_applyPositionOffset.set_start(
                timeout=STD_TIMEOUT, x=3, y=2, z=1.5, u=0.6, v=0.5, w=0.3
            )
            await asyncio.sleep(SHORT_TIMEOUT)
            await self.assert_next_sample(
                topic=self.remote.evt_positionUpdate,
                positionX=position.reportedPosition[0] + 3,
                positionY=position.reportedPosition[1] + 2,
                positionZ=position.reportedPosition[2] + 1.5,
                positionU=position.reportedPosition[3] + 0.6,
                positionV=position.reportedPosition[4] + 0.5,
                positionW=position.reportedPosition[5] + 0.3,
            )

    async def test_pivot(self):
        async with self.make_csc(initial_state=salobj.State.ENABLED, simulation_mode=1):
            self.remote.evt_settingsAppliedPivot.flush()
            await self.remote.cmd_pivot.set_start(
                timeout=STD_TIMEOUT, x=0.3, y=0.7, z=0.2
            )
            await self.assert_next_sample(
                topic=self.remote.evt_settingsAppliedPivot,
                pivotX=0.3,
                pivotY=0.7,
                pivotZ=0.2,
            )

    @parameterized.parameterized.expand(
        [
            "applyPositionLimits",
            "moveToPosition",
            "setMaxSystemSpeeds",
            "applyPositionOffset",
            "pivot",
        ]
    )
    async def test_assert_substate(self, name):
        async with self.make_csc(initial_state=salobj.State.ENABLED, simulation_mode=1):
            await self.csc.report_detailed_state(ATHexapod.DetailedState.INMOTION)
            with salobj.assertRaisesAckError():
                command = getattr(self.remote, f"cmd_{name}")
                await command.set_start(timeout=STD_TIMEOUT)

    async def test_bin_script(self):
        await self.check_bin_script(
            name="ATHexapod",
            index=None,
            exe_name="run_athexapod",
        )
