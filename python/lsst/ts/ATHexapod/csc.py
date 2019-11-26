"""ATHexapod CSC."""
import pathlib

from lsst.ts import salobj
from lsst.ts.idl.enums import ATHexapod


class ATHexapodCSC(salobj.ConfigurableCsc):
    """The class of the ATHexapod CSC.

    Attributes
    ----------
    self.model : `None`
        The model that the CSC interacts with.
    """

    def __init__(self):
        schema_path = pathlib.Path(__file__).resolve().parents[4].joinpath("schema", "ATHexapod.yaml")
        super().__init__(name="ATHexapod", index=None,
                         schema_path=schema_path)
        self.model = None

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
        pass

    async def end_enable(self, id_data):
        """Set the detailed_state as NOTINMOTION.

        Parameters
        ----------
        id_data
        """
        self.detailed_state = ATHexapod.DetailedState.NOTINMOTION

    async def do_applyPositionLimits(self, id_data):
        """Apply the position limits.

        Parameters
        ----------
        id_data
        """
        self.assert_enabled("applyPositionLimits")
        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "applyPositionLimits")
        # add model call

    async def do_moveToPosition(self, id_data):
        """Move the Hexapod to position.

        Parameters
        ----------
        id_data
        """
        self.assert_enabled("moveToPosition")
        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "moveToPosition")
        self.detailed_state = ATHexapod.DetailedState.INMOTION
        # add model call
        self.detailed_state = ATHexapod.DetailedState.NOTINMOTION

    async def do_setMaxSystemSpeeds(self, id_data):
        """Set max system speeds.

        Parameters
        ----------
        id_data
        """
        self.assert_enabled("setMaxSystemSpeeds")
        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "setMaxSystemSpeeds")
        # add model call

    async def do_applyPositionOffset(self, id_data):
        """Apply position offset.

        Parameters
        ----------
        id_data
        """
        self.assert_enabled("applyPositionOffset")
        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "applyPositionOffset")
        # add model call

    async def do_pivot(self, id_data):
        """Pivot the hexapod.

        Parameters
        ----------
        id_data
        """
        self.assert_enabled("pivot")
        self.assert_substate([ATHexapod.DetailedState.NOTINMOTION], "pivot")
        self.detailed_state = ATHexapod.DetailedState.INMOTION
        # add model call
        self.detailed_state = ATHexapod.DetailedState.NOTINMOTION

    async def do_stopAllAxes(self, id_data):
        """Stop all axes.

        Parameters
        ----------
        id_data
        """
        self.assert_enabled("stopAllAxes")
        self.assert_substate([ATHexapod.DetailedState.INMOTION], "stopAllAxes")
        # add model call
        self.detailed_state = ATHexapod.DetailedState.NOTINMOTION

    async def telemetry(self):
        """Handle telemetry publishing."""
        pass
