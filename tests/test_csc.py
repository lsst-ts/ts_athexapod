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
import os
import yaml
import asyncio
import logging
import pathlib
import unittest

from lsst.ts import salobj
from lsst.ts import ATHexapod

import asynctest

STD_TIMEOUT = 15
SHORT_TIMEOUT = 5
TEST_CONFIG_DIR = pathlib.Path(__file__).parents[1].joinpath("tests", "data", "config")


class Harness:
    def __init__(self, initial_state, config_dir=None):
        salobj.set_random_lsst_dds_domain()
        self.csc = ATHexapod.ATHexapodCSC(
            initial_state=initial_state, config_dir=config_dir
        )
        self.remote = salobj.Remote(domain=self.csc.domain, name="ATHexapod", index=0)
        self.server = ATHexapod.MockServer()
        self.log = logging.getLogger(__name__)

    async def __aenter__(self):
        await self.server.start()
        await self.csc.start_task
        return self

    async def __aexit__(self, *args):
        await self.csc.close()
        await self.server.stop()


class CscTestCase(asynctest.TestCase):
    def setUp(self):
        pass

    async def test_configuration(self):
        async with Harness(
            initial_state=salobj.State.STANDBY, config_dir=TEST_CONFIG_DIR
        ) as harness:

            state = await harness.remote.evt_summaryState.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(state.summaryState, salobj.State.STANDBY)

            for bad_config_name in ("no_such_file.yaml", "bad_port.yaml"):
                with self.subTest(bad_config_name=bad_config_name):
                    with salobj.assertRaisesAckError():
                        await harness.remote.cmd_start.set_start(
                            settingsToApply=bad_config_name, timeout=STD_TIMEOUT
                        )

            os.environ["ATHEXAPOD_HOST"] = "127.0.0.1"

            harness.remote.evt_summaryState.flush()

            await harness.remote.cmd_start.set_start(
                settingsToApply="host_as_env.yaml", timeout=STD_TIMEOUT
            )

            state = await harness.remote.evt_summaryState.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(state.summaryState, salobj.State.DISABLED)

            settings = await harness.remote.evt_settingsAppliedTcp.aget(
                timeout=STD_TIMEOUT
            )

            self.assertEqual(settings.ip, os.environ["ATHEXAPOD_HOST"])

            await harness.remote.cmd_standby.start(timeout=STD_TIMEOUT)

            state = await harness.remote.evt_summaryState.aget(timeout=STD_TIMEOUT)
            self.assertEqual(state.summaryState, salobj.State.STANDBY)

            harness.remote.evt_summaryState.flush()

            await harness.remote.cmd_start.set_start(
                settingsToApply="all", timeout=STD_TIMEOUT
            )

            state = await harness.remote.evt_summaryState.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(
                state.summaryState,
                salobj.State.DISABLED,
                f"got {salobj.State(state.summaryState)!r} expected {salobj.State.DISABLED!r}",
            )

            with open(TEST_CONFIG_DIR / "all.yaml") as fp:
                config_all = yaml.load(fp)

            settings_velocity = await harness.remote.evt_settingsAppliedVelocities.aget(
                timeout=STD_TIMEOUT
            )
            settings_pivot = await harness.remote.evt_settingsAppliedPivot.aget(
                timeout=STD_TIMEOUT
            )
            settings_tcp = await harness.remote.evt_settingsAppliedTcp.aget(
                timeout=STD_TIMEOUT
            )

            self.assertEqual(settings_velocity.systemSpeed, config_all["speed"])
            self.assertEqual(settings_pivot.pivotX, config_all["pivot_x"])
            self.assertEqual(settings_pivot.pivotY, config_all["pivot_y"])
            self.assertEqual(settings_pivot.pivotZ, config_all["pivot_z"])
            self.assertEqual(settings_tcp.ip, config_all["host"])
            self.assertEqual(settings_tcp.port, config_all["port"])

    async def test_standard_state_transitions(self):
        async with Harness(initial_state=salobj.State.STANDBY) as harness:
            state = await harness.remote.evt_summaryState.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(state.summaryState, salobj.State.STANDBY)

            await harness.remote.cmd_start.start()
            self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
            state = await harness.remote.evt_summaryState.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(state.summaryState, salobj.State.DISABLED)

            await harness.remote.cmd_enable.start()
            self.assertEqual(harness.csc.summary_state, salobj.State.ENABLED)
            state = await harness.remote.evt_summaryState.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(state.summaryState, salobj.State.ENABLED)

            await harness.remote.cmd_disable.start()
            self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
            state = await harness.remote.evt_summaryState.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(state.summaryState, salobj.State.DISABLED)

            await harness.remote.cmd_standby.start()
            self.assertEqual(harness.csc.summary_state, salobj.State.STANDBY)
            state = await harness.remote.evt_summaryState.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(state.summaryState, salobj.State.STANDBY)

    async def test_apply_position_limits(self):
        async with Harness(initial_state=salobj.State.STANDBY) as harness:
            await harness.remote.cmd_start.start(timeout=STD_TIMEOUT)
            await harness.remote.cmd_enable.start(timeout=STD_TIMEOUT)
            await harness.remote.evt_settingsAppliedPositionLimits.next(
                flush=False, timeout=STD_TIMEOUT
            )
            await harness.remote.cmd_applyPositionLimits.set_start(
                timeout=STD_TIMEOUT, xyMax=12, zMin=-6, zMax=8, uvMax=5, wMin=-3, wMax=7
            )
            event = await harness.remote.evt_settingsAppliedPositionLimits.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(12, event.limitXYMax)
            self.assertEqual(-6, event.limitZMin)
            self.assertEqual(8, event.limitZMax)
            self.assertEqual(5, event.limitUVMax)
            self.assertEqual(-3, event.limitWMin)
            self.assertEqual(7, event.limitWMax)

    async def test_move_to_position(self):
        async with Harness(initial_state=salobj.State.STANDBY) as harness:
            await harness.remote.cmd_start.start(timeout=STD_TIMEOUT)
            await harness.remote.cmd_enable.start(timeout=STD_TIMEOUT)
            await harness.remote.cmd_moveToPosition.set_start(
                timeout=STD_TIMEOUT, x=4, y=6, z=3, u=4, v=3, w=6
            )
            await asyncio.sleep(SHORT_TIMEOUT)
            event = await harness.remote.evt_inPosition.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(False, event.inPosition)
            event = await harness.remote.evt_inPosition.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(True, event.inPosition)
            event = await harness.remote.evt_positionUpdate.aget(timeout=STD_TIMEOUT)
            self.assertEqual(4, event.positionX)
            self.assertEqual(6, event.positionY)
            self.assertEqual(3, event.positionZ)
            self.assertEqual(4, event.positionU)
            self.assertEqual(3, event.positionV)
            self.assertEqual(6, event.positionW)

    async def test_set_max_system_speeds(self):
        async with Harness(initial_state=salobj.State.STANDBY) as harness:
            await harness.remote.cmd_start.start(timeout=STD_TIMEOUT)
            await harness.remote.cmd_enable.start(timeout=STD_TIMEOUT)
            await harness.remote.cmd_setMaxSystemSpeeds.set_start(
                timeout=STD_TIMEOUT, speed=1
            )
            event = await harness.remote.evt_settingsAppliedVelocities.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(1, event.systemSpeed)

    async def test_apply_position_offset(self):
        async with Harness(initial_state=salobj.State.STANDBY) as harness:
            await harness.remote.cmd_start.start(timeout=STD_TIMEOUT)
            await harness.remote.cmd_enable.start(timeout=STD_TIMEOUT)
            position = await harness.remote.tel_positionStatus.aget()
            await harness.remote.cmd_applyPositionOffset.set_start(
                timeout=STD_TIMEOUT, x=3, y=2, z=1.5, u=0.6, v=0.5, w=0.3
            )
            await asyncio.sleep(SHORT_TIMEOUT)
            event = await harness.remote.evt_positionUpdate.aget()
            self.assertEqual(3 + position.reportedPosition[0], event.positionX)
            self.assertEqual(2 + position.reportedPosition[1], event.positionY)
            self.assertEqual(1.5 + position.reportedPosition[2], event.positionZ)
            self.assertEqual(0.6 + position.reportedPosition[3], event.positionU)
            self.assertEqual(0.5 + position.reportedPosition[4], event.positionV)
            self.assertEqual(0.3 + position.reportedPosition[5], event.positionW)

    async def test_pivot(self):
        async with Harness(initial_state=salobj.State.STANDBY) as harness:
            await harness.remote.cmd_start.start(timeout=STD_TIMEOUT)
            await harness.remote.cmd_enable.start(timeout=STD_TIMEOUT)
            harness.remote.evt_settingsAppliedPivot.flush()
            await harness.remote.cmd_pivot.set_start(
                timeout=STD_TIMEOUT, x=0.3, y=0.7, z=0.2
            )
            event = await harness.remote.evt_settingsAppliedPivot.next(
                flush=False, timeout=STD_TIMEOUT
            )
            self.assertEqual(0.3, event.pivotX)
            self.assertEqual(0.7, event.pivotY)
            self.assertEqual(0.2, event.pivotZ)


if __name__ == "__main__":
    unittest.main()
