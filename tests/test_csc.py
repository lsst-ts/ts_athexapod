import asyncio
import unittest
import logging

from lsst.ts import salobj
from lsst.ts import ATHexapod

STD_TIMEOUT = 45


class Harness:
    def __init__(self, initial_state):
        salobj.test_utils.set_random_lsst_dds_domain()
        self.csc = ATHexapod.ATHexapodCSC(initial_state=initial_state)
        self.csc.model.controller = ATHexapod.MockController(log=None)
        self.remote = salobj.Remote(domain=self.csc.domain, name="ATHexapod", index=0)
        self.log = logging.getLogger(__name__)

    async def __aenter__(self):
        await self.csc.start_task
        return self

    async def __aexit__(self, *args):
        await self.csc.close()


class CscTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_standard_state_transitions(self):
        async def doit():
            async with Harness(initial_state=salobj.State.STANDBY) as harness:
                state = await harness.remote.evt_summaryState.next(flush=False, timeout=STD_TIMEOUT)
                self.assertEqual(state.summaryState, salobj.State.STANDBY)

                await harness.remote.cmd_start.start()
                self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
                state = await harness.remote.evt_summaryState.next(flush=False, timeout=STD_TIMEOUT)
                self.assertEqual(state.summaryState, salobj.State.DISABLED)

                await harness.remote.cmd_enable.start()
                self.assertEqual(harness.csc.summary_state, salobj.State.ENABLED)
                state = await harness.remote.evt_summaryState.next(flush=False, timeout=STD_TIMEOUT)
                self.assertEqual(state.summaryState, salobj.State.ENABLED)

                await harness.remote.cmd_disable.start()
                self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
                state = await harness.remote.evt_summaryState.next(flush=False, timeout=STD_TIMEOUT)
                self.assertEqual(state.summaryState, salobj.State.DISABLED)

                await harness.remote.cmd_standby.start()
                self.assertEqual(harness.csc.summary_state, salobj.State.STANDBY)
                state = await harness.remote.evt_summaryState.next(flush=False, timeout=STD_TIMEOUT)
                self.assertEqual(state.summaryState, salobj.State.STANDBY)

        asyncio.get_event_loop().run_until_complete(doit())

    def test_apply_position_limits(self):
        async def doit():
            async with Harness(initial_state=salobj.State.ENABLED) as harness:
                await harness.remote.cmd_applyPositionLimits.set_start(timeout=STD_TIMEOUT, xyMax=12, zMin=-6,
                                                                       zMax=12, uvMax=8, wMin=-6, wMax=6)
                event = await harness.remote.evt_settingsAppliedPositionLimits.next(flush=False,
                                                                                    timeout=STD_TIMEOUT)
                self.assertEqual(12, event.limitXYMax)
                self.assertEqual(-6, event.limitZMin)
                self.assertEqual(12, event.limitZMax)
                self.assertEqual(8, event.limitUVMax)
                self.assertEqual(-6, event.limitWMin)
                self.assertEqual(6, event.limitWMax)

        asyncio.get_event_loop().run_until_complete(doit())

    @unittest.skip("Shenanigans")
    def test_move_to_position(self):
        async def doit():
            async with Harness(initial_state=salobj.State.DISABLED) as harness:
                await harness.remote.cmd_enable.start(timeout=STD_TIMEOUT)
                await harness.remote.cmd_moveToPosition.set_start(timeout=STD_TIMEOUT, x=4, y=6, z=3, u=4,
                                                                  v=3, w=6)
                event = await harness.remote.evt_inPosition.next(flush=False, timeout=STD_TIMEOUT)
                self.assertEqual(False, event.inPosition)
                event = await harness.remote.evt_inPosition.next(flush=False, timeout=STD_TIMEOUT)
                self.assertEqual(True, event.inPosition)
                event = await harness.remote.evt_positionUpdate.next(flush=True, timeout=STD_TIMEOUT)
                self.assertEqual(4, event.positionX)
                self.assertEqual(6, event.positionY)
                self.assertEqual(3, event.positionZ)
                self.assertEqual(4, event.positionU)
                self.assertEqual(3, event.positionV)
                self.assertEqual(6, event.positionW)

        asyncio.get_event_loop().run_until_complete(doit())

    def test_set_max_system_speeds(self):
        async def doit():
            async with Harness(initial_state=salobj.State.DISABLED) as harness:
                await harness.remote.cmd_enable.start(timeout=STD_TIMEOUT)
                await harness.remote.cmd_setMaxSystemSpeeds.set_start(timeout=STD_TIMEOUT, speed=1)
                event = await harness.remote.evt_settingsAppliedVelocities.next(flush=False,
                                                                                timeout=STD_TIMEOUT)
                self.assertEqual(1, event.systemSpeed)

        asyncio.get_event_loop().run_until_complete(doit())

    def test_apply_position_offset(self):
        async def doit():
            async with Harness(initial_state=salobj.State.DISABLED) as harness:
                await harness.remote.cmd_enable.start(timeout=STD_TIMEOUT)
                await harness.remote.cmd_applyPositionOffset.set_start(timeout=STD_TIMEOUT, x=1, y=1, z=1,
                                                                       u=1, v=1, w=1)

        asyncio.get_event_loop().run_until_complete(doit())

    @unittest.skip("Shenanigans")
    def test_pivot(self):
        async def doit():
            async with Harness(initial_state=salobj.State.DISABLED) as harness:
                await harness.remote.cmd_enable.start(timeout=STD_TIMEOUT)
                await harness.remote.cmd_pivot.set_start(timeout=STD_TIMEOUT, x=1, y=1, z=1)
                event = await harness.remote.evt_settingsAppliedPivot.next(flush=True, timeout=STD_TIMEOUT)
                self.assertEqual(1, event.pivotX)
                self.assertEqual(1, event.pivotY)
                self.assertEqual(1, event.pivotZ)

        asyncio.get_event_loop().run_until_complete(doit())
