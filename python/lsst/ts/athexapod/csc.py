"""
This file is part of ts_ATHexapod

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

__all__ = ["ATHexapodCSC", "execute_csc"]

import asyncio
import os
import traceback
import types
import pathlib

from lsst.ts import salobj
from lsst.ts import utils
from lsst.ts.xml.enums import ATHexapod
from lsst.ts.xml import sal_enums as sal_enums

from . import __version__
from .config_schema import CONFIG_SCHEMA
from .controller import ATHexapodController
from .gcserror import translate_error
from .mock_server import MockServer
from .wizardry import LONG_TIMEOUT

CONNECTION_FAILED = 100
TEL_LOOP_CLOSED = 101
CONTROLLER_NOT_READY = 102
REFERENCING_TIMEOUT = 103
REFERENCING_ERROR = 104


def execute_csc() -> None:
    asyncio.run(ATHexapodCSC.amain(index=None))


class ATHexapodCSC(salobj.ConfigurableCsc):
    """The class of the ATHexapod CSC.

    Parameters
    ----------
    config_dir : `pathlib.Path`
        The directory where the configurations for the ATHexapod reside.
        Found in ts_config_attcs under ATHexapod directory.
    initial_state : `salobj.State`
        The inital state that the CSC starts in.
    simulation_mode : `int`
        Whether the csc starts in simulation mode or not.

    Attributes
    ----------
    controller : `None`
        The controller that the CSC interacts with.
    config : `dict`
        A dictionary of parsed yaml that provides configuration information
        for the CSC.
    run_telemetry_task : `bool`
        Whether the telemetry should run or not.
    telemetry_task : `asyncio.Task`
        The task that handles telemetry.
    """

    valid_simulation_modes = [0, 1]
    version: str = __version__

    def __init__(
        self,
        config_dir: None | pathlib.Path | str = None,
        initial_state: None | sal_enums.State | int = sal_enums.State.STANDBY,
        simulation_mode: int = 0,
    ):
        super().__init__(
            name="ATHexapod",
            index=0,
            config_dir=config_dir,
            initial_state=initial_state,
            simulation_mode=simulation_mode,
            config_schema=CONFIG_SCHEMA,
        )

        self._detailed_state: ATHexapod.DetailedState = ATHexapod.DetailedState.NOTINMOTION
        self.config: None | types.SimpleNamespace = None
        self.controller: None | ATHexapodController = None

        self.run_telemetry_task: bool = False
        self.telemetry_task: asyncio.Future = utils.make_done_future()

        self._ready: bool = False
        self.mock_server: None | MockServer = None

    @property
    def ready(self) -> bool:
        """Returns the state of the ATHexapod as ready or not.

        Publishes any change in readiness as an event over SAL

        Returns
        -------
            ready : `bool`
                If true, the Hexapod is ready or if false, the Hexapod is not
                ready.

        """
        return self.evt_readyForCommand.data.ready

    async def report_new_ready(self, ready: bool) -> None:
        """Report the new ready state of the ATHexapod"""
        await self.evt_readyForCommand.set_write(ready=bool(ready))

    def assert_substate(self, substates: list[ATHexapod.DetailedState], action: str) -> None:
        """Assert that the command is in a valid substate.

        Parameters
        ----------
        substates : `List of Str`
            A list of valid substates.
        action : `str`
            The name of the command being checked.
        """
        if self.detailed_state not in [ATHexapod.DetailedState(substate) for substate in substates]:
            raise salobj.ExpectedError(f"{action} not allowed in {self.detailed_state}")

    @property
    def detailed_state(self) -> ATHexapod.DetailedState:
        """Return the substate of the CSC.

        Returns
        -------
        detailed_state : `ATHexapod.DetailedState`
            The validated substate of the CSC.
        """
        return self.evt_detailedState.data.detailedState

    async def report_detailed_state(self, new_detailed_state: ATHexapod.DetailedState) -> None:
        """Publish the new detailed state."""
        new_detailed_state = ATHexapod.DetailedState(new_detailed_state)
        await self.evt_detailedState.set_write(detailedState=new_detailed_state)

    def get_config_pkg(self) -> str:
        """Return the name of the config directory for the ATHexapod CSC."""
        return "ts_config_attcs"

    async def configure(self, config: types.SimpleNamespace) -> None:
        """Configure the CSC.

        Parameters
        ----------
        config
        """
        host = config.host
        if host.startswith("ENV."):
            env_name = host.split("ENV.")[1]
            if env_name not in os.environ:
                raise RuntimeError(f"Failed to configure CSC.Environment variable {env_name} is not defined.")
            host = os.environ[env_name]
            self.log.debug(f"Reading hexapod controller host from environment variable. {env_name}={host}.")
        self.host = host

        self.config = config

        await self.evt_settingsAppliedVelocities.set_write(systemSpeed=self.config.speed)

        await self.evt_settingsAppliedPivot.set_write(
            pivotX=self.config.pivot_x,
            pivotY=self.config.pivot_y,
            pivotZ=self.config.pivot_z,
        )

        await self.evt_settingsAppliedTcp.set_write(ip=self.host, port=self.config.port)

    async def begin_start(self, data: salobj.BaseMsgType) -> None:
        """Execute before state transition from STANDBY to DISABLE.

        Send a ack_in_progress for waiting for connection to device.
        """
        await self.cmd_start.ack_in_progress(
            data=data,
            timeout=LONG_TIMEOUT,
            result="Waiting for device connection",
        )
        if self.simulation_mode and self.mock_server is None:
            self.mock_server = MockServer(port=50000)
            await self.mock_server.start_task
        await super().begin_start(data)

    async def end_start(self, data: salobj.BaseMsgType) -> None:
        """Execute after state transition from STANDBY to DISABLE.

        It will attempt to connect to the hexapod controller and start the
        telemetry loop. Transition to `FAULT` if it fails.

        Parameters
        ----------
        data

        """
        assert self.config is not None
        self.controller = ATHexapodController(
            log=self.log, host=self.host, port=self.config.port, timeout=self.config.movement_timeout
        )
        if self.mock_server is not None:
            self.controller.port = self.mock_server.port
        try:
            await self.controller.connect()
        except Exception as e:
            self.log.exception(e)
            raise e

        self.run_telemetry_task = True
        self.telemetry_task = asyncio.create_task(self.telemetry())

        await super().end_start(data)

    async def end_standby(self, data: salobj.BaseMsgType) -> None:
        """Executes after transition from DISABLE to STANDBY.

        It will stop the telemetry loop and disconnect from the hexapod
        controller.
        """
        await self.cmd_standby.ack_in_progress(
            data, LONG_TIMEOUT, result="Waiting for disconnection."
        )
        try:
            await self.close_telemetry_task()
        except Exception:
            self.log.exception("Exception closing telemetry task.")

        if self.controller is not None:
            try:
                await self.controller.disconnect()
                self.controller = None
            except Exception:
                self.log.exception("Exception disconnecting from hexapod controller.")

        if self.mock_server is not None:
            await self.mock_server.close()
            await self.mock_server.done_task
            self.mock_server = None

        await super().end_standby(data)

    async def end_enable(self, data: salobj.BaseMsgType) -> None:
        """Executed after state is enabled.

        This may cause the hexapod to move.

        Actions performed by this task are:

        1. - Set soft limits on the hexapod controller.
        2. - Check that the hexapod axis are referenced.
        3. - If axis are not referenced and `auto_reference=True`, will
             reference axis.

        The CSC will reject attempts to move axis that are not referenced.

        Parameters
        ----------
        data
        """
        await self.report_new_ready(False)
        await self.report_detailed_state(ATHexapod.DetailedState.NOTINMOTION)

        # Set soft limits
        assert self.config is not None
        await self.set_limits(
            self.config.limit_xy_max,
            self.config.limit_z_min,
            self.config.limit_z_max,
            self.config.limit_uv_max,
            self.config.limit_w_min,
            self.config.limit_w_max,
        )

        try:
            await self.assert_ready("enable")
        except salobj.base.ExpectedError:
            self.log.exception("Hexapod controller not ready.")
            await self.fault(
                code=CONTROLLER_NOT_READY,
                report="Hexapod controller not ready.",
                traceback=traceback.format_exc(),
            )

        ref = await self.is_referenced()

        if not ref:
            self.log.warning("Referencing Axis.")
            assert self.controller is not None
            await self.controller.reference()
            await self.report_detailed_state(ATHexapod.DetailedState.INMOTION)
            try:
                await asyncio.wait_for(self.wait_movement_done(), timeout=self.config.reference_timeout)
            except asyncio.TimeoutError as e:
                self.log.error("Referencing time out.")
                self.log.exception(e)
                await self.fault(
                    code=REFERENCING_TIMEOUT,
                    report="Referencing time out.",
                    traceback=traceback.format_exc(),
                )
            except Exception as e:
                self.log.error("Exception happened while referencing.")
                self.log.exception(e)
                await self.fault(
                    code=REFERENCING_ERROR,
                    report="Exception happened while referencing hexapod.",
                    traceback=traceback.format_exc(),
                )
        assert self.controller is not None
        current_position = await self.controller.real_position()

        await self.evt_positionUpdate.set_write(
            positionX=current_position[0],
            positionY=current_position[1],
            positionZ=current_position[2],
            positionU=current_position[3],
            positionV=current_position[4],
            positionW=current_position[5],
        )

        await super().end_enable(data)

    async def set_limits(
        self,
        xy_max: float,
        limit_z_min: float,
        limit_z_max: float,
        limit_uv_max: float,
        limit_w_min: float,
        limit_w_max: float,
    ) -> None:
        """Set limits and publish events.

        Parameters
        ----------
        xy_max : `float`
        limit_z_min : `float`
        limit_z_max : `float`
        limit_uv_max : `float`
        limit_w_min : `float`
        limit_w_max : `float`

        Returns
        -------
        None
        """
        assert self.controller is not None
        await self.controller.set_low_position_soft_Limit(
            -xy_max, -xy_max, limit_z_min, -limit_uv_max, -limit_uv_max, limit_w_min
        )

        await self.controller.set_high_position_soft_limit(
            xy_max, xy_max, limit_z_max, limit_uv_max, limit_uv_max, limit_w_max
        )

        await self.evt_settingsAppliedPositionLimits.set_write(
            limitXYMax=xy_max,
            limitZMin=limit_z_min,
            limitZMax=limit_z_max,
            limitUVMax=limit_uv_max,
            limitWMin=limit_w_min,
            limitWMax=limit_w_max,
        )

    async def do_applyPositionLimits(self, data: salobj.BaseMsgType) -> None:
        """Apply the position limits.

        Parameters
        ----------
        data
        """
        self.assert_enabled("applyPositionLimits")
        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "applyPositionLimits")

        await self.set_limits(data.xyMax, data.zMin, data.zMax, data.uvMax, data.wMin, data.wMax)

    async def do_moveToPosition(self, data: salobj.BaseMsgType) -> None:
        """Move the Hexapod to position.

        Parameters
        ----------
        data
        """
        self.assert_enabled("moveToPosition")
        await self.assert_ready("moveToPosition")
        await self.assert_referenced("moveToPosition")
        assert self.controller is not None

        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "moveToPosition")

        await self.report_detailed_state(ATHexapod.DetailedState.INMOTION)
        await self.evt_inPosition.set_write(inPosition=False, force_output=True)

        await self.controller.set_position(data.x, data.y, data.z, data.u, data.v, data.w)
        assert self.config is not None

        try:
            await asyncio.wait_for(self.wait_movement_done(), timeout=self.config.movement_timeout)
        except Exception as e:
            self.log.exception("Error executing moveToPosition command")
            raise e
        else:
            await self.evt_inPosition.set_write(inPosition=True, force_output=True)
        finally:
            await self.report_detailed_state(ATHexapod.DetailedState.NOTINMOTION)

            current_position = await self.controller.real_position()

            await self.evt_positionUpdate.set_write(
                positionX=current_position[0],
                positionY=current_position[1],
                positionZ=current_position[2],
                positionU=current_position[3],
                positionV=current_position[4],
                positionW=current_position[5],
            )

    async def do_setMaxSystemSpeeds(self, data: salobj.BaseMsgType) -> None:
        """Set max system speeds.

        Parameters
        ----------
        data
        """
        self.assert_enabled("setMaxSystemSpeeds")
        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "setMaxSystemSpeeds")
        assert self.controller is not None
        await self.controller.set_sv(velocity=data.speed)
        current_sv = await self.controller.get_sv()
        await self.evt_settingsAppliedVelocities.set_write(systemSpeed=current_sv)

    async def do_applyPositionOffset(self, data: salobj.BaseMsgType) -> None:
        """Apply position offset.

        Parameters
        ----------
        data
        """
        self.assert_enabled("applyPositionOffset")
        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "applyPositionOffset")
        await self.report_detailed_state(ATHexapod.DetailedState.INMOTION)
        assert self.controller is not None
        await self.controller.offset(data.x, data.y, data.z, data.u, data.v, data.w)
        assert self.config is not None
        await asyncio.wait_for(self.wait_movement_done(), self.config.movement_timeout)
        await self.evt_inPosition.set_write(inPosition=True, force_output=True)
        await self.report_detailed_state(ATHexapod.DetailedState.NOTINMOTION)
        current_position = await self.controller.real_position()
        await self.evt_positionUpdate.set_write(
            positionX=current_position[0],
            positionY=current_position[1],
            positionZ=current_position[2],
            positionU=current_position[3],
            positionV=current_position[4],
            positionW=current_position[5],
        )

    async def do_pivot(self, data: salobj.BaseMsgType) -> None:
        """Set pivot point of the hexapod.

        Parameters
        ----------
        data
        """
        self.assert_enabled("pivot")
        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "pivot")
        assert self.controller is not None
        await self.controller.set_pivot_point(data.x, data.y, data.z)
        current_pivot = await self.controller.getPivotPoint()
        await self.evt_settingsAppliedPivot.set_write(
            pivotX=current_pivot[0], pivotY=current_pivot[1], pivotZ=current_pivot[2]
        )

    async def do_stopAllAxes(self, data: salobj.BaseMsgType) -> None:
        """Stop all axes.

        Parameters
        ----------
        data
        """
        self.assert_enabled("stopAllAxes")
        assert self.controller is not None
        await self.controller.stop_all_axes()
        await self.report_detailed_state(ATHexapod.DetailedState.NOTINMOTION)

    async def telemetry(self) -> None:
        """Handle telemetry publishing.

        Publish tel_positionStatus

        """

        sub_tasks = 2
        while self.run_telemetry_task:
            assert self.controller is not None
            if not self.controller.is_connected and self.controller.client.should_be_connected:
                await self.fault(code=CONNECTION_FAILED, report="Connection lost.")
                self.run_telemetry_task = False
            # Get setpointPosition
            target_position = await self.controller.target_position()

            # Get reportedPosition
            current_position = await self.controller.real_position()

            diff = [current_position[i] - target_position[i] for i in range(6)]

            await self.tel_positionStatus.set_write(
                setpointPosition=target_position,
                reportedPosition=current_position,
                positionFollowingError=diff,
            )

            await asyncio.sleep(self.heartbeat_interval / sub_tasks)

            # Check for errors
            error = await self.controller.get_error()
            if error != 0:
                await self.fault(code=error, report=translate_error(error), traceback="")
                self.run_telemetry_task = False
            else:
                await asyncio.sleep(self.heartbeat_interval / sub_tasks)

        if self.disabled_or_enabled:
            await self.fault(
                code=TEL_LOOP_CLOSED,
                report=f"Telemetry loop closing while in {self.summary_state!r}.",
                traceback="",
            )

    async def close_telemetry_task(self) -> None:
        """Tries to close telemetry task gracefully.

        If it fails to close it gracefully, cancels it.
        """
        self.run_telemetry_task = False

        if self.telemetry_task.done():
            self.log.debug("Telemetry task already completed. Nothing to do...")
            return

        try:
            await asyncio.wait_for(self.telemetry_task, timeout=2 * self.heartbeat_interval)
        except asyncio.TimeoutError:
            self.log.warning("Timed out waiting for telemetry task to finish. Canceling task instead.")
            await self._cancel_telemetry_task()
        except Exception:
            self.log.exception("Unexpected exception stopping telemetry task. Closing task instead.")
            await self._cancel_telemetry_task()

    async def _cancel_telemetry_task(self) -> None:
        """Cancel telemetry task and handle cancellation."""
        if self.telemetry_task.done():
            self.log.debug("Telemetry task already completed. Nothing to do...")
            return

        self.telemetry_task.cancel()
        try:
            await self.telemetry_task
        except asyncio.CancelledError:
            self.log.debug("Telemetry task cancelled.")
        except Exception:
            self.log.exception("Unexpected exception closing telemetry task.")

    async def assert_ready(self, action: str) -> None:
        """Assert that the Hexapod is ready.

        Parameters
        ----------
        action : `str`
            The name of the action that requires the Hexapod to be ready.
        """
        assert self.controller is not None
        ready = await self.controller.controller_ready()

        if ready != self.ready:
            await self.report_new_ready(ready)

        if not self.ready:
            # raise salobj.base.ExpectedError(f"{action} not allowed.
            # Controller not ready.")
            self.log.debug(f"{action} not allowed. Controller not ready.")

    async def assert_referenced(self, action: str) -> None:
        """Assert that the Hexapod is referenced.

        Parameters
        ----------
        action : `str`
            The action that requires the Hexapod to be referenced.
        """
        assert self.controller is not None
        ref = await self.controller.referencing_result()

        if not all(ref):
            axis = "XYZUVW"
            not_referenced = ""
            for i in range(len(ref)):
                if not ref[i]:
                    not_referenced += axis[i]

            raise salobj.base.ExpectedError(
                f"{action} not allowed. Axis {not_referenced} "
                f"not referenced. Re-cycle CSC state to reference axis."
            )

    async def is_referenced(self) -> bool:
        """Checks if Hexapod is referenced."""
        assert self.controller is not None
        ref = await self.controller.referencing_result()

        return all(ref)

    async def wait_movement_done(self) -> bool:
        """Wait for the Hexapod movement to be done."""
        axis = "XYZUVW"

        while True:
            try:
                assert self.controller is not None
                ms = await self.controller.motion_status()

                if not any(ms):
                    self.log.debug("Hexapod not moving.")
                    await self.report_detailed_state(ATHexapod.DetailedState.NOTINMOTION)
                    return not (any(ms))
                else:
                    await self.report_detailed_state(ATHexapod.DetailedState.INMOTION)
                    moving = ""
                    for i in range(len(ms)):
                        if ms[i]:
                            moving += axis[i]
                    self.log.debug(f"Hexapod axis {moving} moving.")
            except Exception as e:
                self.log.error("Could not get motion status.")
                self.log.exception(e)

            await asyncio.sleep(self.heartbeat_interval)

    async def close_tasks(self) -> None:
        await super().close_tasks()
        await self.close_telemetry_task()
        if self.controller is not None and self.controller.is_connected:
            await self.controller.disconnect()
        if self.mock_server is not None:
            await self.mock_server.close()
            await self.mock_server.done_task
            self.mock_server = None
