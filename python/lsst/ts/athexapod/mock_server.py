"""
This file is part of ts_ATHexapod

Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
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

import logging
import re
import types
from typing import Awaitable, Callable

from lsst.ts import simactuators
from lsst.ts import tcpip


class MockServer(tcpip.OneClientReadLoopServer):
    """_summary_

    Parameters
    ----------
    port : `int`
        The port that the server starts on, defaults to 0.
    """

    def __init__(self, port: int = 0) -> None:
        self.device: HexapodDevice = HexapodDevice()
        log = logging.getLogger(__name__)
        super().__init__(port=port, log=log, terminator=b"\n", encoding="ISO-8859-1")

    async def read_and_dispatch(self) -> None:
        """Read and parse message and return a response if any."""
        line = await self.read_str()
        self.log.debug(f"{line=}")
        response = await self.device.parse_message(line)
        self.log.debug(f"{response=}")
        if response is not None:
            await self.write_str(response)


class HexapodDevice:
    """Implement a fake PI Hexapod controller."""

    def __init__(self) -> None:
        self.log: logging.Logger = logging.getLogger(__name__)
        self.ready: bool = False
        self.x: simactuators.PointToPointActuator = simactuators.PointToPointActuator(
            min_position=-12.6, max_position=22.6, speed=1
        )
        self.y: simactuators.PointToPointActuator = simactuators.PointToPointActuator(
            min_position=-12.6, max_position=22.6, speed=1
        )
        self.z: simactuators.PointToPointActuator = simactuators.PointToPointActuator(
            min_position=-12.6, max_position=12.6, speed=1
        )
        self.u: simactuators.PointToPointActuator = simactuators.PointToPointActuator(
            min_position=-7.6, max_position=7.6, speed=1
        )
        self.v: simactuators.PointToPointActuator = simactuators.PointToPointActuator(
            min_position=-7.6, max_position=7.6, speed=1
        )
        self.w: simactuators.PointToPointActuator = simactuators.PointToPointActuator(
            min_position=-12.6, max_position=12.6, speed=1
        )
        self.referenced: types.SimpleNamespace = types.SimpleNamespace(x=0, y=0, z=0, u=0, v=0, w=0)
        self.sv: int = 1
        self.pivot: types.SimpleNamespace = types.SimpleNamespace(x=0, y=0, z=0, u=0, v=0, w=0)
        self.command_calls: dict[str, Callable[..., Awaitable[None | str]]] = {
            "\3": self.format_real_position,
            "\5": self.format_motion_status,
            "\7": self.format_controller_ready,
            "MOV": self.set_position,
            "FRF?": self.format_referencing_result,
            "FRF": self.reference,
            "MOV?": self.format_target_position,
            "ERR?": self.format_error,
            "NLM": self.set_low_position_soft_Limit,
            "NLM?": self.format_low_position_soft_limit,
            "PLM": self.set_high_position_soft_limit,
            "PLM?": self.format_high_position_soft_limit,
            "SPI": self.set_pivot_point,
            "SPI?": self.format_pivot_point,
            "VLS": self.set_sv,
            "VLS?": self.format_sv,
            "MVR": self.format_offset,
        }
        self.commands: list[re.Pattern[str]] = [
            re.compile("^(?P<cmd>\3)$"),
            re.compile("^(?P<cmd>\5)$"),
            re.compile("^(?P<cmd>\6)$"),
            re.compile("^(?P<cmd>\7)$"),
            re.compile(
                (
                    r"^(?P<cmd>MOV) (?P<x>X) (?P<x_value>\d+.\d+) "
                    r"(?P<y>Y) (?P<y_value>\d+.\d+) (?P<z>Z) (?P<z_value>\d+.\d+) "
                    r"(?P<u>U) (?P<u_value>\d+.\d+) (?P<v>V) (?P<v_value>\d+.\d+) "
                    r"(?P<w>W) (?P<w_value>\d+.\d+)$"
                )
            ),
            re.compile(r"^(?P<cmd>FRF\?)$"),
            re.compile(r"^(?P<cmd>FRF) X Y Z U V W$"),
            re.compile(r"^(?P<cmd>MOV\?) X Y Z U V W$"),
            re.compile(r"^(?P<cmd>ERR\?)$"),
            re.compile(
                (
                    r"^(?P<cmd>NLM) (?P<x>X) (?P<x_value>-\d+.\d+) (?P<y>Y) (?P<y_value>-\d+.\d+) "
                    r"(?P<z>Z) (?P<z_value>-\d+.\d+) (?P<u>U) (?P<u_value>-\d+.\d+) "
                    r"(?P<v>V) (?P<v_value>-\d+.\d+) (?P<w>W) (?P<w_value>-\d+.\d+)$"
                )
            ),
            re.compile(r"^(?P<cmd>NLM\?) X Y Z U V W$"),
            re.compile(
                (
                    r"^(?P<cmd>PLM) (?P<x>X) (?P<x_value>\d+.\d+) (?P<y>Y) (?P<y_value>\d+.\d+) "
                    r"(?P<z>Z) (?P<z_value>\d+.\d+) (?P<u>U) (?P<u_value>\d+.\d+) "
                    r"(?P<v>V) (?P<v_value>\d+.\d+) (?P<w>W) (?P<w_value>\d+.\d+)$"
                )
            ),
            re.compile(r"^(?P<cmd>PLM\?) X Y Z U V W$"),
            re.compile(
                (
                    r"^(?P<cmd>SPI) (?P<x>X) (?P<x_value>\d+.\d+) "
                    r"(?P<y>Y) (?P<y_value>\d+.\d+) (?P<z>Z) (?P<z_value>\d+.\d+)$"
                )
            ),
            re.compile(r"^(?P<cmd>SPI\?)$"),
            re.compile(r"^(?P<cmd>VLS) (?P<velocity>\d+.\d+)$"),
            re.compile(r"^(?P<cmd>VLS\?)$"),
            re.compile(
                (
                    r"^(?P<cmd>MVR) (?P<x>X) (?P<x_value>\d+.\d+) "
                    r"(?P<y>Y) (?P<y_value>\d+.\d+) (?P<z>Z) (?P<z_value>\d+.\d+) "
                    r"(?P<u>U) (?P<u_value>\d+.\d+) (?P<v>V) (?P<v_value>\d+.\d+) "
                    r"(?P<w>W) (?P<w_value>\d+.\d+)$"
                )
            ),
        ]

    async def parse_message(self, line: str) -> None | str:
        """Parse the message and return a response if any.

        Parameters
        ----------
        line : str
            The command received.

        Returns
        -------
        Optional[str]
            Returns a string response if expected.

        Raises
        ------
        Exception
            Raised if command is not implemented.
        """
        for command in self.commands:
            matched_command = command.match(line)
            if matched_command:
                self.log.debug(f"Matched command {line}")
                command_group = matched_command.group("cmd")
                if command_group in self.command_calls:
                    called_command = self.command_calls[command_group]
                    self.log.debug(f"cmd group:{command_group}")
                    if command_group in ["NLM", "MOV", "PLM", "MVR"]:
                        self.log.debug(f"Grabbing command {command_group}")
                        response = await called_command(
                            x=float(matched_command.group("x_value")),
                            y=float(matched_command.group("y_value")),
                            z=float(matched_command.group("z_value")),
                            u=float(matched_command.group("u_value")),
                            v=float(matched_command.group("v_value")),
                            w=float(matched_command.group("w_value")),
                        )
                        return response
                    elif command_group in ["SPI"]:
                        self.log.debug(f"Grabbing command {command_group}")
                        response = await called_command(
                            x=float(matched_command.group("x_value")),
                            y=float(matched_command.group("y_value")),
                            z=float(matched_command.group("z_value")),
                        )
                        return response
                    elif command_group in ["VLS"]:
                        self.log.debug(f"Grabbing command {command_group}")
                        response = await called_command(velocity=float(matched_command.group("velocity")))
                        return response
                    else:
                        self.log.debug(f"{command_group=}")
                        response = await called_command()
                        self.log.debug(f"{response=}")
                        return response
                else:
                    raise Exception(f"{command_group} is not implemented.")
        return None

    async def format_real_position(self) -> str:
        """Return formatted position response."""
        return (
            f"X={self.x.position()}\n "
            f"Y={self.y.position()}\n "
            f"Z={self.z.position()}\n "
            f"U={self.u.position()}\n "
            f"V={self.v.position()}\n "
            f"W={self.w.position()}"
        )

    async def format_motion_status(self) -> str:
        """Return formatted motion status response."""
        motion_string = (
            f"{int(self.x.moving())}"
            f"{int(self.y.moving())}"
            f"{int(self.z.moving())}"
            f"{int(self.u.moving())}"
            f"{int(self.v.moving())}"
            f"{int(self.w.moving())}"
        )
        motion_bitinteger = int(motion_string, 2)
        return str(motion_bitinteger)

    async def format_controller_ready(self) -> str:
        """Return formatted controller ready response."""
        self.ready = True
        return f"{chr(177)}"

    async def stop_all_axes(self) -> None:
        """Stop all axes.

        Not implemented due to axes not actually moving naturally.
        """
        pass

    async def set_position(self, x: float, y: float, z: float, u: float, v: float, w: float) -> None:
        """Set the position.
        Parameters
        ----------
        x : float
        y : float
        z : float
        u : float
        v : float
        w : float
        """
        self.log.debug("Setting position")
        self.x.set_position(float(x))
        self.y.set_position(float(y))
        self.z.set_position(float(z))
        self.u.set_position(float(u))
        self.v.set_position(float(v))
        self.w.set_position(float(w))

    async def format_referencing_result(self) -> str:
        """Return formatted reference result."""
        return (
            f"X={self.referenced.x}\n "
            f"Y={self.referenced.y}\n "
            f"Z={self.referenced.z}\n "
            f"U={self.referenced.u}\n "
            f"V={self.referenced.v}\n "
            f"W={self.referenced.w}"
        )

    async def reference(self) -> None:
        """Reference the hexapod."""
        self.referenced.x = 1
        self.referenced.y = 1
        self.referenced.z = 1
        self.referenced.u = 1
        self.referenced.v = 1
        self.referenced.w = 1

    async def format_target_position(self) -> str:
        """Return formatted string for target position"""
        return (
            f"X={self.x.end_position}\n "
            f"Y={self.y.end_position}\n "
            f"Z={self.z.end_position}\n "
            f"U={self.u.end_position}\n "
            f"V={self.v.end_position}\n "
            f"W={self.w.end_position}"
        )

    async def set_low_position_soft_Limit(
        self, x: float, y: float, z: float, u: float, v: float, w: float
    ) -> None:
        """Set the lower position software limit.
        Parameters
        ----------
        x : float
            The x axis minimum software limit.
        y : float
            The y axis minimum software limit.
        z : float
            The z axis minimum software limit.
        u : float
            The u axis minimum software limit.
        v : float
            The v axis minimum software limit.
        w : float
            The w axis minimum software limit.
        """
        self.x.min_position = float(x)
        self.y.min_position = float(y)
        self.z.min_position = float(z)
        self.u.min_position = float(u)
        self.v.min_position = float(v)
        self.w.min_position = float(w)

    async def format_low_position_soft_limit(self) -> str:
        """Return formatted lower position software limit string."""
        return (
            f"X={self.x.min_position}\n "
            f"Y={self.y.min_position}\n "
            f"Z={self.z.min_position}\n "
            f"U={self.u.min_position}\n "
            f"V={self.v.min_position}\n "
            f"W={self.w.min_position}"
        )

    async def set_high_position_soft_limit(
        self, x: float, y: float, z: float, u: float, v: float, w: float
    ) -> None:
        """Set higher position software limit.
        Parameters
        ----------
        x : float
        y : float
        z : float
        u : float
        v : float
        w : float
        """
        self.x.max_position = float(x)
        self.y.max_position = float(y)
        self.z.max_position = float(z)
        self.u.max_position = float(u)
        self.v.max_position = float(v)
        self.w.max_position = float(w)

    async def format_high_position_soft_limit(self) -> str:
        """Return formatted higher position software limit string."""
        return (
            f"X={self.x.max_position}\n "
            f"Y={self.y.max_position}\n "
            f"Z={self.z.max_position}\n "
            f"U={self.u.max_position}\n "
            f"V={self.v.max_position}\n "
            f"W={self.w.max_position}"
        )

    async def format_on_target(self) -> None:
        """Return formatted on target string.

        Not implemented.
        """
        pass

    async def format_position_unit(self) -> None:
        """Return formatted get position unit string."""
        pass

    async def format_offset(self, x: float, y: float, z: float, u: float, v: float, w: float) -> None:
        """Set offset for hexapod.
        Parameters
        ----------
        x : float
        y : float
        z : float
        u : float
        v : float
        w : float
        """
        self.log.debug("Setting offset.")
        await self.set_position(
            x=self.x.position() + float(x),
            y=self.y.position() + float(y),
            z=self.z.position() + float(z),
            u=self.u.position() + float(u),
            v=self.v.position() + float(v),
            w=self.w.position() + float(w),
        )

    async def check_offset(self, x: float, y: float, z: float, u: float, v: float, w: float) -> str:
        """Check that the hexapod can move.
        Parameters
        ----------
        x : float
        y : float
        z : float
        u : float
        v : float
        w : float
        """
        return "X=1\n Y=1\n Z=1\n U=1\n V=1\n W=1"

    async def set_pivot_point(self, x: float, y: float, z: float) -> None:
        """Set the pivot point.
        Parameters
        ----------
        x : float
        y : float
        z : float
        """
        self.pivot.x = x
        self.pivot.y = y
        self.pivot.z = z

    async def format_pivot_point(self) -> str:
        """Return formatted get pivot point string"""
        return f"R={self.pivot.x}\n S={self.pivot.y}\n T={self.pivot.z}"

    async def format_check_active_soft_limit(self) -> None:
        """Check that the software limits are active."""
        pass

    async def activate_soft_limit(self, x: float, y: float, z: float, u: float, v: float, w: float) -> None:
        """Activate the software limits.
        Parameters
        ----------
        x : float
        y : float
        z : float
        u : float
        v : float
        w : float
        """
        pass

    async def set_clv(self, x: float, y: float, z: float, u: float, v: float, w: float) -> None:
        """Set the closed loop velocity.
        Parameters
        ----------
        x : float
        y : float
        z : float
        u : float
        v : float
        w : float
        """
        pass

    async def format_clv(self) -> None:
        """Return the closed loop velocity."""
        pass

    async def set_sv(self, velocity: int) -> None:
        """Set the system velocity.
        Parameters
        ----------
        velocity : int
        """
        self.sv = velocity

    async def format_sv(self) -> str:
        """Return the system velocity."""
        return f"{self.sv}"

    async def format_error(self) -> str:
        """Return get error string"""
        return "0"
