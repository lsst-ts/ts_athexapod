"""ATHexapod CSC."""

__all__ = ["ATHexapodCSC"]

import asyncio
import pathlib
import traceback

from lsst.ts import salobj
from lsst.ts.idl.enums import ATHexapod

from .model import Model
from .gcserror import translate_error

CONNECTION_FAILED = 100
TEL_LOOP_CLOSED = 101
CONTROLLER_NOT_READY = 102
REFERENCING_TIMEOUT = 103
REFERENCING_ERROR = 104


class ATHexapodCSC(salobj.ConfigurableCsc):
    """The class of the ATHexapod CSC.

    Attributes
    ----------
    self.model : `None`
        The model that the CSC interacts with.
    """

    def __init__(self, config_dir=None,
                 initial_state=salobj.State.STANDBY,
                 simulation_mode=0):

        schema_path = pathlib.Path(__file__).resolve().parents[4].joinpath("schema", "ATHexapod.yaml")

        super().__init__(name="ATHexapod", index=0, config_dir=config_dir,
                         initial_state=initial_state,
                         simulation_mode=simulation_mode,
                         schema_path=schema_path)

        self._detailed_state = ATHexapod.DetailedState.NOTINMOTION
        self.config = None
        self.model = Model(log=self.log)

        self.run_telemetry_task = False
        self.telemetry_task = None

        self._ready = False

    @property
    def ready(self):
        return self._ready

    @ready.setter
    def ready(self, ready):
        self._ready = bool(ready)
        self.evt_readyForCommand.set_put(ready=self._ready)

    def assert_substate(self, substates, action):
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
    def detailed_state(self):
        """Return the substate of the CSC.

        Parameters
        ----------
        sub_state : `ATHexapod.DetailedState`
            The sub_state to be set to.

        Returns
        -------
        detailed_state : `ATHexapod.DetailedState`
            The validated substate of the CSC.
        """
        return self._detailed_state

    @detailed_state.setter
    def detailed_state(self, sub_state):
        self._detailed_state = ATHexapod.DetailedState(sub_state)
        self.report_detailed_state()

    def report_detailed_state(self):
        """Publish the new detailed state."""
        self.evt_detailedState.set_put(detailedState=self.detailed_state)

    def get_config_pkg(self):
        """Return the name of the config directory for the ATHexapod CSC."""
        return "ts_config_attcs"

    async def configure(self, config):
        """Configure the CSC.

        Parameters
        ----------
        config
        """
        self.model.host = config.host
        self.model.port = config.port
        self.model.timeout = config.connection_timeout

        self.config = config

        self.evt_settingsAppliedVelocities.set_put(systemSpeed=self.config.speed)

        self.evt_settingsAppliedPivot.set_put(pivotX=self.config.pivot_x,
                                              pivotY=self.config.pivot_y,
                                              pivotZ=self.config.pivot_z)

        self.evt_settingsAppliedTcp.set_put(ip=self.config.host,
                                            port=self.config.port)

    async def end_start(self, data):
        """ Execute after state transition from STANDBY to DISABLE.

        It will attempt to connect to the hexapod controller and start the
        telemetry loop. Transition to `FAULT` if it fails.

        Parameters
        ----------
        data

        """
        try:
            await self.model.connect()
        except Exception as e:
            self.log.exception(e)
            self.fault(code=CONNECTION_FAILED,
                       report=f'Could not connect to hexapod controller with IP/Port: '
                              f'{self.model.host}/{self.model.port}.',
                       traceback=traceback.format_exc())
            raise e

        self.run_telemetry_task = True
        self.telemetry_task = asyncio.create_task(self.telemetry())

        await super().end_start(data)

    async def end_standby(self, data):
        """ Executes after transition from DISABLE to STANDBY.

        If will stop the telemetry loop and disconnect from the hexapod
        controller.
        """

        try:
            await self.close_telemetry_task()
        except Exception as e:
            self.log.error("Exception closing telemetry task.")
            self.log.exception(e)

        try:
            await self.model.disconnect()
        except Exception as e:
            self.log.error("Exception disconnecting from hexapod controller.")
            self.log.exception(e)

        await super().end_standby(data)

    async def end_enable(self, data):
        """ Executed after state is enabled.

        This may cause the hexapod to move.

        Actions performed by this task are:

        1 - Set soft limits on the hexapod controller.
        2 - Check that the hexapod axis are referenced.
        3 - If axis are not referenced and `auto_reference=True`, will
            reference axis.

        The CSC will reject attempts to move axis that are not referenced.

        Parameters
        ----------
        data
        """
        self.ready = False
        self.detailed_state = ATHexapod.DetailedState.NOTINMOTION

        # Set soft limits

        await self.set_limits(self.config.limit_xy_max,
                              self.config.limit_z_min, self.config.limit_z_max,
                              self.config.limit_uv_max,
                              self.config.limit_w_min, self.config.limit_w_max)

        try:
            await self.assert_ready("enable")
        except salobj.base.ExpectedError as e:
            self.log.error("Hexapod controller not ready.")
            self.log.exception(e)
            self.fault(code=CONTROLLER_NOT_READY,
                       report="Hexapod controller not ready.",
                       traceback=traceback.format_exc())

        ref = await self.is_referenced()

        if not ref:
            self.log.warning("Referencing Axis.")
            await self.model.reference()
            self.detailed_state = ATHexapod.DetailedState.INMOTION
            try:
                await asyncio.wait_for(self.wait_movement_done(),
                                       timeout=self.config.reference_timeout)
            except asyncio.TimeoutError as e:
                self.log.error("Referencing time out.")
                self.log.exception(e)
                self.fault(code=REFERENCING_TIMEOUT,
                           report="Referencing time out.",
                           traceback=traceback.format_exc())
            except Exception as e:
                self.log.error("Exception happened while referencing.")
                self.log.exception(e)
                self.fault(code=REFERENCING_ERROR,
                           report="Exception happened while referencing hexapod.",
                           traceback=traceback.format_exc())

        current_position = await self.model.real_position()

        self.evt_positionUpdate.set_put(positionX=current_position[0],
                                        positionY=current_position[1],
                                        positionZ=current_position[2],
                                        positionU=current_position[3],
                                        positionV=current_position[4],
                                        positionW=current_position[5])

        await super().end_enable(data)

    async def set_limits(self, xy_max, limit_z_min, limit_z_max,
                         limit_uv_max, limit_w_min, limit_w_max):
        """ Set limits and publish events.

        Parameters
        ----------
        xy_max
        limit_z_min
        limit_z_max
        limit_uv_max
        limit_w_min
        limit_w_max

        Returns
        -------

        """

        await self.model.set_low_position_soft_Limit(-xy_max, -xy_max, limit_z_min,
                                                     -limit_uv_max, -limit_uv_max, limit_w_min)

        await self.model.set_high_position_soft_limit(xy_max, xy_max, limit_z_max,
                                                      limit_uv_max, limit_uv_max, limit_w_max)

        self.evt_settingsAppliedPositionLimits.set_put(limitXYMax=self.config.limit_xy_max,
                                                       limitZMin=self.config.limit_z_min,
                                                       limitZMax=self.config.limit_z_max,
                                                       limitUVMax=self.config.limit_uv_max,
                                                       limitWMin=self.config.limit_w_min,
                                                       limitWMax=self.config.limit_w_max)

    async def do_applyPositionLimits(self, data):
        """Apply the position limits.

        Parameters
        ----------
        data
        """
        self.assert_enabled("applyPositionLimits")
        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "applyPositionLimits")

        await self.set_limits(self.config.limit_xy_max,
                              self.config.limit_z_min, self.config.limit_z_max,
                              self.config.limit_uv_max,
                              self.config.limit_w_min, self.config.limit_w_max)

    async def do_moveToPosition(self, data):
        """Move the Hexapod to position.

        Parameters
        ----------
        data
        """
        self.assert_enabled("moveToPosition")
        await self.assert_ready("moveToPosition")
        await self.assert_referenced("moveToPosition")

        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "moveToPosition")

        self.detailed_state = ATHexapod.DetailedState.INMOTION
        self.evt_inPosition.set_put(inPosition=False,
                                    force_output=True)

        await self.model.set_position(data.x, data.y, data.z,
                                      data.u, data.v, data.w)

        try:
            await asyncio.wait_for(self.wait_movement_done(),
                                   timeout=self.config.movement_timeout)
        except Exception as e:
            self.log.error("Error executing moveToPosition command")
            raise e
        else:
            self.evt_inPosition.set_put(inPosition=True,
                                        force_output=True)
        finally:
            self.detailed_state = ATHexapod.DetailedState.NOTINMOTION

            current_position = await self.model.real_position()

            self.evt_positionUpdate.set_put(positionX=current_position[0],
                                            positionY=current_position[1],
                                            positionZ=current_position[2],
                                            positionU=current_position[3],
                                            positionV=current_position[4],
                                            positionW=current_position[5])

    async def do_setMaxSystemSpeeds(self, data):
        """Set max system speeds.

        Parameters
        ----------
        data
        """
        raise NotImplementedError("setMaxSystemSpeeds command not implemented.")

    async def do_applyPositionOffset(self, data):
        """Apply position offset.

        Parameters
        ----------
        data
        """
        raise NotImplementedError("applyPositionOffset command not implemented.")
        # add model call

    async def do_pivot(self, data):
        """Pivot the hexapod.

        Parameters
        ----------
        data
        """
        raise NotImplementedError("pivot command not implemented.")

    async def do_stopAllAxes(self, data):
        """Stop all axes.

        Parameters
        ----------
        data
        """
        self.assert_enabled("stopAllAxes")
        await self.model.stop_all_axes()
        self.detailed_state = ATHexapod.DetailedState.NOTINMOTION

    async def telemetry(self):
        """Handle telemetry publishing.

        Publish tel_positionStatus

        """

        sub_tasks = 2
        while self.run_telemetry_task:

            # Get setpointPosition
            target_position = await self.model.target_position()

            # Get reportedPosition
            current_position = await self.model.real_position()

            diff = [current_position[i]-target_position[i] for i in range(6)]

            self.tel_positionStatus.set_put(setpointPosition=target_position,
                                            reportedPosition=current_position,
                                            positionFollowingError=diff)

            await asyncio.sleep(self.heartbeat_interval/sub_tasks)

            # Check for errors
            error = await self.model.get_error()
            if error != 0:
                self.fault(code=error,
                           report=translate_error(error),
                           traceback="")
                self.run_telemetry_task = False
            else:
                await asyncio.sleep(self.heartbeat_interval/sub_tasks)

        if self.disabled_or_enabled:
            self.fault(code=TEL_LOOP_CLOSED,
                       report=f"Telemetry loop closing while in {self.summary_state!r}.",
                       traceback="")

    async def close_telemetry_task(self):
        """Tries to close telemetry task gracefully.

        If it fails to close it gracefully, cancels it.
        """
        self.run_telemetry_task = False

        force_close = False

        try:
            await asyncio.wait_for(self.telemetry_task,
                                   timeout=2 * self.heartbeat_interval)
        except asyncio.TimeoutError:
            self.log.warning("Timed out waiting for telemetry task to finish. "
                             "Closing task instead.")
            force_close = True
        except Exception as e:
            self.log.error("Unexpected exception stopping telemetry task. "
                           "Closing task instead.")
            self.log.exception(e)
            force_close = True

        if force_close:
            self.telemetry_task.cancel()
            try:
                await self.telemetry_task
            except asyncio.CancelledError:
                self.log.debug("Telemetry task cancelled.")
            except Exception as e:
                self.log.error("Unexpected exception closing telemetry task.")
                self.log.exception(e)

        self.telemetry_task = None

    async def assert_ready(self, action):
        ready = await self.model.controller_ready()

        if ready != self.ready:
            self.ready = ready

        if not self.ready:
            # raise salobj.base.ExpectedError(f"{action} not allowed. Controller not ready.")
            self.log.debug(f"{action} not allowed. Controller not ready.")

    async def assert_referenced(self, action):

        ref = await self.model.referencing_result()

        if not all(ref):
            axis = "XYZUVW"
            not_referenced = ""
            for i in range(len(ref)):
                if not ref[i]:
                    not_referenced += axis[i]

            raise salobj.base.ExpectedError(f"{action} not allowed. Axis {not_referenced} "
                                            f"not referenced. Re-cycle CSC state to reference axis.")

    async def is_referenced(self):

        ref = await self.model.referencing_result()

        return all(ref)

    async def wait_movement_done(self):

        axis = "XYZUVW"

        while True:

            try:
                ms = await self.model.motion_status()

                if not any(ms):
                    self.log.debug("Hexapod not moving.")
                    self.detailed_state = ATHexapod.DetailedState.NOTINMOTION
                    return not(any(ms))
                else:
                    self.detailed_state = ATHexapod.DetailedState.INMOTION
                    moving = ''
                    for i in range(len(ms)):
                        if ms[i]:
                            moving += axis[i]
                    self.log.debug(f"Hexapod axis {moving} moving.")
            except Exception as e:
                self.log.error("Could not get motion status.")
                self.log.exception(e)

            await asyncio.sleep(self.heartbeat_interval)
