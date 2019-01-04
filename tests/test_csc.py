#!/usr/bin/env python

import asyncio
import time
import unittest

import numpy as np

try:
    import SALPY_ATHexapod
except ImportError:
    SALPY_ATHexapod = None

from lsst.ts import salobj
from lsst.ts.ATHexapod import ATHexapodCSC

np.random.seed(47)


def fillWithRandom(data, lowValue, highValue):
    reservedFields = ['action', 'device', 'itemValue', 'property']

    for field in dir(data):
        if not field.startswith('__') and field not in reservedFields:
            print('fill :', field)
            setattr(data, field, np.random.uniform(lowValue, highValue))


class Harness:
    def __init__(self, initial_state):
        index = 0
        self.csc = ATHexapodCSC.ATHexapodCsc(index, initial_state=initial_state)
        self.remote = salobj.Remote(SALPY_ATHexapod, index)
        salobj.test_utils.set_random_lsst_dds_domain()


class CommunicateTestCase(unittest.TestCase):
    # @unittest.skip("demonstrating skipping")
    def test_heartbeat(self):
        async def doit():
            harness = Harness(initial_state=salobj.State.STANDBY)
            start_time = time.time()
            await harness.remote.evt_heartbeat.next(flush=True, timeout=2)
            await harness.remote.evt_heartbeat.next(flush=True, timeout=2)
            duration = time.time() - start_time
            self.assertLess(abs(duration - 2), 1.5)  # not clear what this limit should be

        asyncio.get_event_loop().run_until_complete(doit())

    # @unittest.skip("demonstrating skipping")
    def test_main(self):
        async def doit():
            index = 0
            process = await asyncio.create_subprocess_exec("../bin.src/runATHexapodCSC.py", str(index))
            try:
                remote = salobj.Remote(SALPY_ATHexapod, index)
                summaryState_data = await remote.evt_summaryState.next(flush=False, timeout=10)
                self.assertEqual(summaryState_data.summaryState, salobj.State.STANDBY)
                remote.evt_summaryState.flush()
                id_ack = await remote.cmd_exitControl.start(remote.cmd_exitControl.DataType(), timeout=2)
                self.assertEqual(id_ack.ack.ack, remote.salinfo.lib.SAL__CMD_COMPLETE)
                summaryState_data = await remote.evt_summaryState.next(flush=False, timeout=10)
                self.assertEqual(summaryState_data.summaryState, salobj.State.OFFLINE)

                await asyncio.wait_for(process.wait(), 2)
            except Exception:
                if process.returncode is None:
                    process.terminate()
                raise

        asyncio.get_event_loop().run_until_complete(doit())

    # @unittest.skip("Skip to run tests 1 by 1 during development...")
    def test_applyPositionLimits_command(self):
        """Update the position limits through cmd_applyPositionLimits and then listen to 
        evt_settingsAppliedPositionLimits to check if the limits were applied.
        """
        async def doit():
            harness = await self.beginningFunc()

            # send the applyPositionLimits command with random data
            cmd_data_sent = self.make_random_cmd_applyPositionLimits(harness)
            # set a long timeout here to allow for simulated hardware delay inside the CSC
            task = harness.remote.evt_settingsAppliedPositionLimits.next(flush=True, timeout=30)
            # Check if applied is being published
            task2 = harness.remote.evt_appliedSettingsMatchStart.next(flush=True, timeout=30)

            await harness.remote.cmd_applyPositionLimits.start(cmd_data_sent, timeout=30)

            # see if new data was broadcast correctly
            evt_data = await task
            evt2_data = await task2
            self.assertEqual(evt2_data.appliedSettingsMatchStartIsTrue, 0)

            print('cmd_data_sent:')
            for prop in dir(cmd_data_sent):
                if not prop.startswith('__'):
                    print(prop, getattr(cmd_data_sent, prop))

            print('evt_data:')
            for prop in dir(evt_data):
                if not prop.startswith('__'):
                    print(prop, getattr(evt_data, prop))

            # Check that they are the same
            self.assertAlmostEqual(cmd_data_sent.uvMax, evt_data.limitUVMax, places=4)
            self.assertAlmostEqual(cmd_data_sent.wMax, evt_data.limitWMax, places=4)
            self.assertAlmostEqual(cmd_data_sent.wMin, evt_data.limitWMin, places=4)
            self.assertAlmostEqual(cmd_data_sent.xyMax, evt_data.limitXYMax, places=4)
            self.assertAlmostEqual(cmd_data_sent.zMax, evt_data.limitZMax, places=4)
            self.assertAlmostEqual(cmd_data_sent.zMin, evt_data.limitZMin, places=4)

            await self.endFunc(harness)

        asyncio.get_event_loop().run_until_complete(doit())

    # @unittest.skip("Skip to run tests 1 by 1 during development...")
    def test_moveToPosition_command(self):
        """Move to a random position and then compare the commanded position to the position read on the device
        """

        async def doit():
            harness = await self.beginningFunc()

            # send the moveToPosition command with random data
            cmd_data_sent = self.make_random_cmd_moveToPosition(harness)

            task = harness.remote.evt_positionUpdate.next(flush=True, timeout=30)
            # set a long timeout here to allow for hexapod to get to the commanded position
            await harness.remote.cmd_moveToPosition.start(cmd_data_sent, timeout=600)
            # see if new data was broadcast correctly
            evt_data = await task
            # get las position update
            tel_data = await harness.remote.tel_positionStatus.next(flush=True, timeout=30)

            print('cmd_data_sent:')
            for prop in dir(cmd_data_sent):
                if not prop.startswith('__'):
                    print(prop, getattr(cmd_data_sent, prop))

            print('evt_data:')
            for prop in dir(evt_data):
                if not prop.startswith('__'):
                    print(prop, getattr(evt_data, prop))

            print('tel_data:')
            for prop in dir(tel_data):
                if not prop.startswith('__'):
                    print(prop, getattr(tel_data, prop))

            # Check that the commanded position is the same as the target published
            self.assertAlmostEqual(cmd_data_sent.x, evt_data.positionX, places=4)
            self.assertAlmostEqual(cmd_data_sent.y, evt_data.positionY, places=4)
            self.assertAlmostEqual(cmd_data_sent.z, evt_data.positionZ, places=4)
            self.assertAlmostEqual(cmd_data_sent.u, evt_data.positionU, places=4)
            self.assertAlmostEqual(cmd_data_sent.v, evt_data.positionV, places=4)
            self.assertAlmostEqual(cmd_data_sent.w, evt_data.positionW, places=4)

            # Check that the real position is the same as the commanded
            self.assertAlmostEqual(cmd_data_sent.x, tel_data.reportedPosition[0], places=4)
            self.assertAlmostEqual(cmd_data_sent.y, tel_data.reportedPosition[1], places=4)
            self.assertAlmostEqual(cmd_data_sent.z, tel_data.reportedPosition[2], places=4)
            self.assertAlmostEqual(cmd_data_sent.u, tel_data.reportedPosition[3], places=4)
            self.assertAlmostEqual(cmd_data_sent.v, tel_data.reportedPosition[4], places=4)
            self.assertAlmostEqual(cmd_data_sent.w, tel_data.reportedPosition[5], places=4)

            # Check that the target position is the same as the commanded
            self.assertAlmostEqual(cmd_data_sent.x, tel_data.setpointPosition[0], places=4)
            self.assertAlmostEqual(cmd_data_sent.y, tel_data.setpointPosition[1], places=4)
            self.assertAlmostEqual(cmd_data_sent.z, tel_data.setpointPosition[2], places=4)
            self.assertAlmostEqual(cmd_data_sent.u, tel_data.setpointPosition[3], places=4)
            self.assertAlmostEqual(cmd_data_sent.v, tel_data.setpointPosition[4], places=4)
            self.assertAlmostEqual(cmd_data_sent.w, tel_data.setpointPosition[5], places=4)

            await self.endFunc(harness)

        asyncio.get_event_loop().run_until_complete(doit())

    # @unittest.skip("Skip to run tests 1 by 1 during development...")
    def test_moveOffset_command(self):
        """Move offset twice and everytime checks if the hexapod move a difference in position commanded.
        """
        async def doit():
            harness = await self.beginningFunc()

            # send the applyPositionOffset command with random data
            cmd_data_sent = self.make_random_cmd_moveOffset(harness)
            await self.moveOffsetAndValidate(harness, cmd_data_sent)

            cmd_data_sent = self.make_random_cmd_moveOffset(harness)
            await self.moveOffsetAndValidate(harness, cmd_data_sent)

            await self.endFunc(harness)

        asyncio.get_event_loop().run_until_complete(doit())

    # @unittest.skip("Skip to run tests 1 by 1 during development...")
    def test_limits_command(self):
        """Send commands out of range and check if the command is rejected
        """
        async def doit():
            harness = await self.beginningFunc()
            ack = None

            # Test unrealistic values to move offset for X
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_applyPositionOffset.DataType()
                cmd_data_sent.x = 100
                ack = await harness.remote.cmd_applyPositionOffset.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # Test unrealistic values to move offset for Y
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_applyPositionOffset.DataType()
                cmd_data_sent.y = 100
                ack = await harness.remote.cmd_applyPositionOffset.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # Test unrealistic values to move offset for Z
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_applyPositionOffset.DataType()
                cmd_data_sent.z = 100
                ack = await harness.remote.cmd_applyPositionOffset.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # Test unrealistic values to move offset for U
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_applyPositionOffset.DataType()
                cmd_data_sent.u = 100
                ack = await harness.remote.cmd_applyPositionOffset.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # est unrealistic values to move offset for V
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_applyPositionOffset.DataType()
                cmd_data_sent.v = 100
                ack = await harness.remote.cmd_applyPositionOffset.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # est unrealistic values to move offset for W
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_applyPositionOffset.DataType()
                cmd_data_sent.w = 100
                ack = await harness.remote.cmd_applyPositionOffset.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # Test unrealistic values to move to position for X
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_moveToPosition.DataType()
                cmd_data_sent.x = 100
                ack = await harness.remote.cmd_moveToPosition.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # Test unrealistic values to move to position for Y
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_moveToPosition.DataType()
                cmd_data_sent.y = 100
                ack = await harness.remote.cmd_moveToPosition.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # Test unrealistic values to move to position for Z
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_moveToPosition.DataType()
                cmd_data_sent.z = 100
                ack = await harness.remote.cmd_moveToPosition.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # Test unrealistic values to move to position for U
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_moveToPosition.DataType()
                cmd_data_sent.u = 100
                ack = await harness.remote.cmd_moveToPosition.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # est unrealistic values to move to position for V
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_moveToPosition.DataType()
                cmd_data_sent.v = 100
                ack = await harness.remote.cmd_moveToPosition.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            # est unrealistic values to move to position for W
            with self.assertRaises(Exception) as context:
                # send the applyPositionOffset command with random data
                cmd_data_sent = harness.remote.cmd_moveToPosition.DataType()
                cmd_data_sent.w = 100
                ack = await harness.remote.cmd_moveToPosition.start(cmd_data_sent, timeout=600)

            print(str(context.exception))
            self.assertTrue('-302' in str(context.exception))

            await self.endFunc(harness)

        asyncio.get_event_loop().run_until_complete(doit())

    # @unittest.skip("Skip to run tests 1 by 1 during development...")
    def test_pivot_command(self):
        """Send pivot commands and check that events appliedSettingsMatchStart is set false and settingsAppliedPivot
        have the same values as the commanded
        """
        async def doit():
            harness = await self.beginningFunc()

            cmd_data_sent = self.make_random_cmd_pivot(harness)
            taskAppStgMatch = harness.remote.evt_appliedSettingsMatchStart.next(flush=True, timeout=30)
            taskPivot = harness.remote.evt_settingsAppliedPivot.next(flush=True, timeout=30)
            ack = await harness.remote.cmd_pivot.start(cmd_data_sent, timeout=600)
            print("Pivot command:")
            self.printAll(cmd_data_sent)

            # Validate settingsApplied has been published
            evt1_data = await taskPivot
            print("Pivot event:")
            self.printAll(evt1_data)
            self.assertAlmostEqual(evt1_data.pivotX, cmd_data_sent.x, places=3)
            self.assertAlmostEqual(evt1_data.pivotY, cmd_data_sent.y, places=3)
            self.assertAlmostEqual(evt1_data.pivotZ, cmd_data_sent.z, places=3)

            # Validate appliedSettingsMatchStartIsTrue has been updated
            evt2_data = await taskAppStgMatch
            self.assertEqual(evt2_data.appliedSettingsMatchStartIsTrue, 0)

            cmd_data_sent = self.make_random_cmd_pivot(harness)
            print("Pivot command:")
            self.printAll(cmd_data_sent)

            taskPivot = harness.remote.evt_settingsAppliedPivot.next(flush=True, timeout=30)
            ack = await harness.remote.cmd_pivot.start(cmd_data_sent, timeout=600)

            # Validate settingsApplied has been published
            evt1_data = await taskPivot
            print("Pivot event:")
            self.printAll(evt1_data)
            self.assertAlmostEqual(evt1_data.pivotX, cmd_data_sent.x, places=3)
            self.assertAlmostEqual(evt1_data.pivotY, cmd_data_sent.y, places=3)
            self.assertAlmostEqual(evt1_data.pivotZ, cmd_data_sent.z, places=3)

            await self.endFunc(harness)

        asyncio.get_event_loop().run_until_complete(doit())

    # @unittest.skip("demonstrating skipping")
    def test_standard_state_transitions(self):
        """Test standard CSC state transitions.

        The initial state is STANDBY.
        The standard commands and associated state transitions are:

        * start: STANDBY to DISABLED
        * enable: DISABLED to ENABLED

        * disable: ENABLED to DISABLED
        * standby: DISABLED to STANDBY
        * exitControl: STANDBY, FAULT to OFFLINE (quit)
        """
        async def doit():
            harness = Harness(initial_state=salobj.State.STANDBY)
            commands = ("start", "enable", "disable", "exitControl", "standby",
                        "applyPositionLimits", "moveToPosition", "setMaxSpeeds",
                        "applyPositionOffset", "stopAllAxes", "pivot")
            self.assertEqual(harness.csc.summary_state, salobj.State.STANDBY)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
            self.assertEqual(state.summaryState, salobj.State.STANDBY)

            for bad_command in commands:
                if bad_command in ("start", "exitControl"):
                    continue  # valid command in STANDBY state
                with self.subTest(bad_command=bad_command):
                    print('From STANDBY: ', bad_command)
                    cmd_attr = getattr(harness.remote, f"cmd_{bad_command}")
                    with salobj.test_utils.assertRaisesAckError(
                            ack=harness.remote.salinfo.lib.SAL__CMD_FAILED):
                        await cmd_attr.start(cmd_attr.DataType())

            # send start; new state is DISABLED
            cmd_attr = getattr(harness.remote, f"cmd_start")
            cmd_attr_dataType = cmd_attr.DataType()
            setattr(cmd_attr_dataType, "settingsToApply", "Default2")
            id_ack = await cmd_attr.start(cmd_attr_dataType)
            self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
            self.assertEqual(id_ack.ack.error, 0)

            self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
            self.assertEqual(state.summaryState, salobj.State.DISABLED)

            for bad_command in commands:
                if bad_command in ("enable", "standby"):
                    continue  # valid command in DISABLED state
                with self.subTest(bad_command=bad_command):
                    cmd_attr = getattr(harness.remote, f"cmd_{bad_command}")
                    with salobj.test_utils.assertRaisesAckError(
                            ack=harness.remote.salinfo.lib.SAL__CMD_FAILED):
                        await cmd_attr.start(cmd_attr.DataType())

            # send enable; new state is ENABLED
            cmd_attr = getattr(harness.remote, f"cmd_enable")
            id_ack = await cmd_attr.start(cmd_attr.DataType())
            self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
            self.assertEqual(id_ack.ack.error, 0)
            self.assertEqual(harness.csc.summary_state, salobj.State.ENABLED)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
            self.assertEqual(state.summaryState, salobj.State.ENABLED)

            for bad_command in commands:
                if bad_command in ("disable", "applyPositionLimits", "moveToPosition", "setMaxSpeeds",
                                   "applyPositionOffset", "stopAllAxes", "pivot"):
                    continue  # valid command in DISABLED state
                with self.subTest(bad_command=bad_command):
                    cmd_attr = getattr(harness.remote, f"cmd_{bad_command}")
                    with salobj.test_utils.assertRaisesAckError(
                            ack=harness.remote.salinfo.lib.SAL__CMD_FAILED):
                        await cmd_attr.start(cmd_attr.DataType())

            # send disable; new state is DISABLED
            cmd_attr = getattr(harness.remote, f"cmd_disable")
            id_ack = await cmd_attr.start(cmd_attr.DataType())
            self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
            self.assertEqual(id_ack.ack.error, 0)
            self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
            self.assertEqual(state.summaryState, salobj.State.DISABLED)

            # send standby; new state is STANDBY
            cmd_attr = getattr(harness.remote, f"cmd_standby")
            id_ack = await cmd_attr.start(cmd_attr.DataType())
            self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
            self.assertEqual(id_ack.ack.error, 0)
            self.assertEqual(harness.csc.summary_state, salobj.State.STANDBY)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
            self.assertEqual(state.summaryState, salobj.State.STANDBY)

            # send exitControl; new state is OFFLINE
            cmd_attr = getattr(harness.remote, f"cmd_exitControl")
            id_ack = await cmd_attr.start(cmd_attr.DataType())
            self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
            self.assertEqual(id_ack.ack.error, 0)
            self.assertEqual(harness.csc.summary_state, salobj.State.OFFLINE)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
            self.assertEqual(state.summaryState, salobj.State.OFFLINE)

            await asyncio.wait_for(harness.csc.done_task, 2)

        asyncio.get_event_loop().run_until_complete(doit())

    def printAll(self, data):
        for prop in dir(data):
            if not prop.startswith('__'):
                print(prop, getattr(data, prop))

    async def moveOffsetAndValidate(self, harness, offset):
            # Get current position
            tel_data = await harness.remote.tel_positionStatus.next(flush=True, timeout=30)
            # Not really getting last value, added a second get to clean last value
            tel_data = await harness.remote.tel_positionStatus.next(flush=True, timeout=30)
            tel_data = await harness.remote.tel_positionStatus.next(flush=True, timeout=30)
            currentX = tel_data.reportedPosition[0]
            currentY = tel_data.reportedPosition[1]
            currentZ = tel_data.reportedPosition[2]
            currentU = tel_data.reportedPosition[3]
            currentV = tel_data.reportedPosition[4]
            currentW = tel_data.reportedPosition[5]
            print('tel_data:')

            print('tel_data:')
            for prop in dir(tel_data):
                if not prop.startswith('__'):
                    print(prop, getattr(tel_data, prop))

            calculatedNewcurrentX = offset.x + currentX
            calculatedNewcurrentY = offset.y + currentY
            calculatedNewcurrentZ = offset.z + currentZ
            calculatedNewcurrentU = offset.u + currentU
            calculatedNewcurrentV = offset.v + currentV
            calculatedNewcurrentW = offset.w + currentW

            task = harness.remote.evt_positionUpdate.next(flush=True, timeout=30)
            # set a long timeout here to allow for hexapod to get to the commanded position
            await harness.remote.cmd_applyPositionOffset.start(offset, timeout=600)
            # see if new data was broadcast correctly
            evt_data = await task
            # get last position update
            tel_data = await harness.remote.tel_positionStatus.next(flush=True, timeout=30)

            print('cmd_data_offset_sent:')
            for prop in dir(offset):
                if not prop.startswith('__'):
                    print(prop, getattr(offset, prop))

            print('evt_data:')
            for prop in dir(evt_data):
                if not prop.startswith('__'):
                    print(prop, getattr(evt_data, prop))

            print('tel_data:')
            for prop in dir(tel_data):
                if not prop.startswith('__'):
                    print(prop, getattr(tel_data, prop))

            # Check that the commanded position is the same as the target published
            self.assertAlmostEqual(calculatedNewcurrentX, evt_data.positionX, places=4)
            self.assertAlmostEqual(calculatedNewcurrentY, evt_data.positionY, places=4)
            self.assertAlmostEqual(calculatedNewcurrentZ, evt_data.positionZ, places=4)
            self.assertAlmostEqual(calculatedNewcurrentU, evt_data.positionU, places=4)
            self.assertAlmostEqual(calculatedNewcurrentV, evt_data.positionV, places=4)
            self.assertAlmostEqual(calculatedNewcurrentW, evt_data.positionW, places=4)

            # Check that the real position is the same as the commanded
            self.assertAlmostEqual(calculatedNewcurrentX, tel_data.reportedPosition[0], places=4)
            self.assertAlmostEqual(calculatedNewcurrentY, tel_data.reportedPosition[1], places=4)
            self.assertAlmostEqual(calculatedNewcurrentZ, tel_data.reportedPosition[2], places=4)
            self.assertAlmostEqual(calculatedNewcurrentU, tel_data.reportedPosition[3], places=4)
            self.assertAlmostEqual(calculatedNewcurrentV, tel_data.reportedPosition[4], places=4)
            self.assertAlmostEqual(calculatedNewcurrentW, tel_data.reportedPosition[5], places=4)

            # Check that the target position is the same as the commanded
            self.assertAlmostEqual(calculatedNewcurrentX, tel_data.setpointPosition[0], places=4)
            self.assertAlmostEqual(calculatedNewcurrentY, tel_data.setpointPosition[1], places=4)
            self.assertAlmostEqual(calculatedNewcurrentZ, tel_data.setpointPosition[2], places=4)
            self.assertAlmostEqual(calculatedNewcurrentU, tel_data.setpointPosition[3], places=4)
            self.assertAlmostEqual(calculatedNewcurrentV, tel_data.setpointPosition[4], places=4)
            self.assertAlmostEqual(calculatedNewcurrentW, tel_data.setpointPosition[5], places=4)

    async def beginningFunc(self):
            harness = Harness(initial_state=salobj.State.STANDBY)
            self.assertIsNone(harness.remote.evt_positionUpdate.get())
            self.assertIsNone(harness.remote.tel_positionStatus.get())

            # Check summaryState
            self.assertEqual(harness.csc.summary_state, salobj.State.STANDBY)
            state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
            self.assertEqual(state.summaryState, salobj.State.STANDBY)
            # Go to enable
            await self.goto_Disable_from_Standby(harness)
            await self.goto_Enable_from_Disable(harness)

            return harness

    async def endFunc(self, harness):
            # Go to standby
            await self.goto_Disable_from_Enable(harness)
            await self.goto_Standby_from_Disable(harness)

    def make_random_cmd_applyPositionLimits(self, harness):
        data = harness.remote.cmd_applyPositionLimits.DataType()
        fillWithRandom(data, -10.0, 10.0)
        data.uvMax = abs(data.uvMax)
        data.wMax = abs(data.wMax)
        data.wMin = -abs(data.wMin)
        data.xyMax = abs(data.xyMax)
        data.zMax = abs(data.zMax)
        data.zMin = -abs(data.zMin)
        return data

    def make_random_cmd_moveToPosition(self, harness):
        data = harness.remote.cmd_moveToPosition.DataType()
        fillWithRandom(data, -5.0, 5.0)
        return data

    def make_random_cmd_moveOffset(self, harness):
        data = harness.remote.cmd_applyPositionOffset.DataType()
        fillWithRandom(data, -1, 1)
        return data

    def make_random_cmd_pivot(self, harness):
        data = harness.remote.cmd_pivot.DataType()
        fillWithRandom(data, -5, 5)
        return data

    async def goto_Disable_from_Standby(self, harness):
        # send start; new state is DISABLED
        cmd_attr = getattr(harness.remote, f"cmd_start")
        cmd_attr_dataType = cmd_attr.DataType()
        setattr(cmd_attr_dataType, "settingsToApply", "Default1")
        id_ack = await cmd_attr.start(cmd_attr_dataType)
        self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
        self.assertEqual(id_ack.ack.error, 0)

        self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
        state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
        self.assertEqual(state.summaryState, salobj.State.DISABLED)

    async def goto_Enable_from_Disable(self, harness):
        # send enable; new state is ENABLED
        cmd_attr = getattr(harness.remote, f"cmd_enable")
        id_ack = await cmd_attr.start(cmd_attr.DataType())
        self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
        self.assertEqual(id_ack.ack.error, 0)
        self.assertEqual(harness.csc.summary_state, salobj.State.ENABLED)
        state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
        self.assertEqual(state.summaryState, salobj.State.ENABLED)

    async def goto_Disable_from_Enable(self, harness):
        # send disable; new state is DISABLED
        cmd_attr = getattr(harness.remote, f"cmd_disable")
        id_ack = await cmd_attr.start(cmd_attr.DataType())
        self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
        self.assertEqual(id_ack.ack.error, 0)
        self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
        state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
        self.assertEqual(state.summaryState, salobj.State.DISABLED)

    async def goto_Standby_from_Disable(self, harness):
        # send standby; new state is STANDBY
        cmd_attr = getattr(harness.remote, f"cmd_standby")
        id_ack = await cmd_attr.start(cmd_attr.DataType())
        self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
        self.assertEqual(id_ack.ack.error, 0)
        self.assertEqual(harness.csc.summary_state, salobj.State.STANDBY)
        state = await harness.remote.evt_summaryState.next(flush=False, timeout=2)
        self.assertEqual(state.summaryState, salobj.State.STANDBY)


if __name__ == "__main__":
    unittest.main()
