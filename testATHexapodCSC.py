import asyncio
import time
import unittest

import numpy as np

try:
    import SALPY_ATHexapod
except ImportError:
    SALPY_ATHexapod = None
import salobj
import ATHexapodCSC

np.random.seed(47)

class Harness:
    def __init__(self, initial_state):
        index = None
        self.csc = ATHexapodCSC.ATHexapodCsc(index, initial_state=initial_state)
        self.remote = salobj.Remote(SALPY_ATHexapod, index)


@unittest.skipIf(SALPY_ATHexapod is None, "Could not import SALPY_ATHexapod")
class CommunicateTestCase(unittest.TestCase):
    def test_heartbeat(self):
        async def doit():
            harness = Harness(initial_state=salobj.State.ENABLED)
            start_time = time.time()
            await harness.remote.evt_heartbeat.next(timeout=2)
            await harness.remote.evt_heartbeat.next(timeout=2)
            duration = time.time() - start_time
            self.assertLess(abs(duration - 2), 1.5) # not clear what this limit should be

        asyncio.get_event_loop().run_until_complete(doit())

    @unittest.skip('reason')
    def test_main(self):
        async def doit():
            index = None
            process = await asyncio.create_subprocess_exec("/home/saluser/test/runATHexapodCSC.py", str(index))
            try:
                remote = salobj.Remote(SALPY_ATHexapod, index)
                summaryState_data = await remote.evt_summaryState.next(flush=False, timeout=10)
                self.assertEqual(summaryState_data.summaryState, salobj.State.STANDBY)

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

    def make_random_cmd_applyPositionLimits(self, csc):
        data = csc.cmd_applyPositionLimits.DataType()
        setattr(data, "xyMax", np.random.uniform(-10.0, 10.0))
        setattr(data, "zMin", np.random.uniform(-10.0, 10.0))
        setattr(data, "zMax", np.random.uniform(-10.0, 10.0))
        setattr(data, "uvMax", np.random.uniform(-10.0, 10.0))
        setattr(data, "wMin", np.random.uniform(-10.0, 10.0))
        setattr(data, "wMax", np.random.uniform(-10.0, 10.0))
        return data
    def test_applyPositionLimits_command(self):
        async def doit():
            harness = Harness(initial_state=salobj.State.ENABLED)
            # until the controller gets its first setArrays
            # it will not send any arrays events or telemetry
            self.assertIsNone(harness.remote.evt_settingsAppliedPositions.get())
            self.assertIsNone(harness.remote.tel_timestamp.get()) # not sure this should be here

            # send the applyPositionLimits command with random data
            cmd_data_sent = self.make_random_cmd_applyPositionLimits(harness.csc)
            # set a long timeout here to allow for simulated hardware delay inside the CSC
            await harness.remote.cmd_applyPositionLimits.start(cmd_data_sent, timeout=30)

            # see if new data was broadcast correctly
            evt_data = await harness.remote.evt_settingsAppliedPositions.next(flush=False, timeout=30)

            print('cmd_data_sent:')
            for prop in dir(cmd_data_sent):
                if not prop.startswith('__'):
                    print(prop, getattr(cmd_data_sent, prop))

            print('evt_data:')
            for prop in dir(evt_data):
                if not prop.startswith('__'):
                    print(prop, getattr(evt_data, prop))

        asyncio.get_event_loop().run_until_complete(doit())

    @unittest.skip('reason')
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

            for bad_command in commands:
                if bad_command in ("start", "exitControl"):
                    continue  # valid command in STANDBY state
                with self.subTest(bad_command=bad_command):
                    cmd_attr = getattr(harness.remote, f"cmd_{bad_command}")
                    with salobj.test_utils.assertRaisesAckError(
                            ack=harness.remote.salinfo.lib.SAL__CMD_FAILED):
                        await cmd_attr.start(cmd_attr.DataType())

            # send start; new state is DISABLED
            cmd_attr = getattr(harness.remote, f"cmd_start")
            state_coro = harness.remote.evt_summaryState.next()
            id_ack = await cmd_attr.start(cmd_attr.DataType())
            state = await state_coro
            self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
            self.assertEqual(id_ack.ack.error, 0)
            self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
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
            state_coro = harness.remote.evt_summaryState.next()
            id_ack = await cmd_attr.start(cmd_attr.DataType())
            state = await state_coro
            self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
            self.assertEqual(id_ack.ack.error, 0)
            self.assertEqual(harness.csc.summary_state, salobj.State.ENABLED)
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

            # send standby; new state is STANDBY
            cmd_attr = getattr(harness.remote, f"cmd_standby")
            id_ack = await cmd_attr.start(cmd_attr.DataType())
            self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
            self.assertEqual(id_ack.ack.error, 0)
            self.assertEqual(harness.csc.summary_state, salobj.State.STANDBY)

            # send exitControl; new state is OFFLINE
            cmd_attr = getattr(harness.remote, f"cmd_exitControl")
            id_ack = await cmd_attr.start(cmd_attr.DataType())
            self.assertEqual(id_ack.ack.ack, harness.remote.salinfo.lib.SAL__CMD_COMPLETE)
            self.assertEqual(id_ack.ack.error, 0)
            self.assertEqual(harness.csc.summary_state, salobj.State.OFFLINE)

            await asyncio.wait_for(harness.csc.done_task, 2)

        asyncio.get_event_loop().run_until_complete(doit())


if __name__ == "__main__":
    unittest.main()
