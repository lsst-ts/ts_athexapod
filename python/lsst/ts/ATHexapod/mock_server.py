'''
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
'''

import asyncio
import re
import logging
import types


class MockServer:
    """Mock server for ATHexapod controller.

    A server which mimics responses from the controller by using asyncio's tcp
    connections to read responses and parse them with regular expressions.

    Parameters
    ----------
    log : `logging.Logger`
        A log either created or passed into the constructor.

    Attributes
    ----------
    host : `str`
    port : `int`
    timeout : `int`
    long_timeout : `int`
    connected : `bool`
    ready : `bool`
    x : `int`
    y : `int`
    z : `int`
    u : `int`
    v : `int`
    w : `int`
    target : `types.SimpleNamespace`
    referenced : `types.SimpleNamespace`
    sv : `int`
    pivot : `types.SimpleNamespace`
    command_calls : `dict`
    commands : `list`
    log : `logging.Logger`
    """
    def __init__(self, log=None):
        self.host = '127.0.0.1'
        self.port = 50000
        self.timeout = 2
        self.long_timeout = 30
        self.connected = False
        self.ready = False
        self.x = 0
        self.y = 0
        self.z = 0
        self.u = 0
        self.v = 0
        self.w = 0
        self.target = types.SimpleNamespace(x=0, y=0, z=0, u=0, v=0, w=0)
        self.referenced = types.SimpleNamespace(x=0, y=0, z=0, u=0, v=0, w=0)
        self.sv = 1
        self.pivot = types.SimpleNamespace(x=0, y=0, z=0, u=0, v=0, w=0)
        self.command_calls = {
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
            "MVR": self.format_offset}
        self.commands = [
            re.compile("^(?P<cmd>\3)$"),
            re.compile("^(?P<cmd>\5)$"),
            re.compile("^(?P<cmd>\6)$"),
            re.compile("^(?P<cmd>\7)$"),
            re.compile((r"^(?P<cmd>MOV) (?P<x>X) (?P<x_value>\d+.\d+) "
                        r"(?P<y>Y) (?P<y_value>\d+.\d+) (?P<z>Z) (?P<z_value>\d+.\d+) "
                        r"(?P<u>U) (?P<u_value>\d+.\d+) (?P<v>V) (?P<v_value>\d+.\d+) "
                        r"(?P<w>W) (?P<w_value>\d+.\d+)$")),
            re.compile(r"^(?P<cmd>FRF\?)$"),
            re.compile(r"^(?P<cmd>FRF) X Y Z U V W$"),
            re.compile(r"^(?P<cmd>MOV\?) X Y Z U V W$"),
            re.compile(r"^(?P<cmd>ERR\?)$"),
            re.compile((r"^(?P<cmd>NLM) (?P<x>X) (?P<x_value>-\d+.\d+) (?P<y>Y) (?P<y_value>-\d+.\d+) "
                        r"(?P<z>Z) (?P<z_value>-\d+.\d+) (?P<u>U) (?P<u_value>-\d+.\d+) "
                        r"(?P<v>V) (?P<v_value>-\d+.\d+) (?P<w>W) (?P<w_value>-\d+.\d+)$")),
            re.compile(r"^(?P<cmd>NLM\?) X Y Z U V W$"),
            re.compile((r"^(?P<cmd>PLM) (?P<x>X) (?P<x_value>\d+.\d+) (?P<y>Y) (?P<y_value>\d+.\d+) "
                        r"(?P<z>Z) (?P<z_value>\d+.\d+) (?P<u>U) (?P<u_value>\d+.\d+) "
                        r"(?P<v>V) (?P<v_value>\d+.\d+) (?P<w>W) (?P<w_value>\d+.\d+)$")),
            re.compile(r"^(?P<cmd>PLM\?) X Y Z U V W$"),
            re.compile((r"^(?P<cmd>SPI) (?P<x>X) (?P<x_value>\d+.\d+) "
                        r"(?P<y>Y) (?P<y_value>\d+.\d+) (?P<z>Z) (?P<z_value>\d+.\d+)$")),
            re.compile(r"^(?P<cmd>SPI\?)$"),
            re.compile(r"^(?P<cmd>VLS) (?P<velocity>\d+.\d+)$"),
            re.compile(r"^(?P<cmd>VLS\?)$"),
            re.compile((r"^(?P<cmd>MVR) (?P<x>X) (?P<x_value>\d+.\d+) "
                        r"(?P<y>Y) (?P<y_value>\d+.\d+) (?P<z>Z) (?P<z_value>\d+.\d+) "
                        r"(?P<u>U) (?P<u_value>\d+.\d+) (?P<v>V) (?P<v_value>\d+.\d+) "
                        r"(?P<w>W) (?P<w_value>\d+.\d+)$"))]
        self.log = logging.getLogger(__name__)

    async def start(self):
        """Start the server."""
        self.log.debug("Starting Server")
        self.server = await asyncio.start_server(client_connected_cb=self.cmd_loop,
                                                 host=self.host,
                                                 port=self.port)
        self.log.debug("Server started")

    async def stop(self):
        """Stop the server"""
        self.log.debug("Closing server")
        self.server.close()
        await asyncio.wait_for(self.server.wait_closed(), timeout=5)
        self.log.debug("Server closed")

    async def cmd_loop(self, reader, writer):
        """Handle received commands."""
        while True:
            line = await reader.readline()
            self.log.debug(f"Received: {line}")
            if not line:
                writer.close()
                return
            line = line.decode()
            self.log.debug(f"Decoded line: {line}")
            for command in self.commands:
                matched_command = command.match(line)
                if matched_command:
                    self.log.debug(f"Matched command {line}")
                    command_group = matched_command.group('cmd')
                    if command_group in self.command_calls:
                        called_command = self.command_calls[command_group]
                        self.log.debug(f"cmd group:{command_group}")
                        if command_group in ['NLM', 'MOV', 'PLM', "MVR"]:
                            self.log.debug(f"Grabbing command {command_group}")
                            await called_command(x=matched_command.group('x_value'),
                                                 y=matched_command.group('y_value'),
                                                 z=matched_command.group('z_value'),
                                                 u=matched_command.group('u_value'),
                                                 v=matched_command.group('v_value'),
                                                 w=matched_command.group('w_value'))
                        elif command_group in ['SPI']:
                            self.log.debug(f"Grabbing command {command_group}")
                            await called_command(x=matched_command.group('x_value'),
                                                 y=matched_command.group('y_value'),
                                                 z=matched_command.group('z_value'))
                        elif command_group in ['VLS']:
                            self.log.debug(f"Grabbing command {command_group}")
                            await called_command(velocity=matched_command.group('velocity'))
                        elif await called_command() is not None:
                            self.log.debug(f"Sent {await called_command()}")
                            writer.write((await called_command()).encode())
                            await writer.drain()
                    else:
                        raise Exception(f"{command_group} is not implemented.")

    async def format_real_position(self):
        """Return formatted position response."""
        return f"X={self.x}\n Y={self.y}\n Z={self.z}\n U={self.u}\n V={self.v}\n W={self.w}\n"

    async def format_motion_status(self):
        """Return formatted motion status response."""
        return f"0\n"

    async def format_controller_ready(self):
        """Return formatted controller ready response."""
        self.ready = True
        return f"{chr(177)}\n"

    async def stop_all_axes(self):
        """Stop all axes.

        Not implemented due to axes not actually moving naturally.
        """
        pass

    async def set_position(self, x, y, z, u, v, w):
        """Set the position."""
        self.log.debug("Setting position")
        self.target.x = x
        self.target.y = y
        self.target.z = z
        self.target.u = u
        self.target.v = v
        self.target.w = w
        self.x = x
        self.y = y
        self.z = z
        self.u = u
        self.v = v
        self.w = w

    async def format_referencing_result(self):
        """Return formatted reference result."""
        return (f"X={self.referenced.x}\n "
                f"Y={self.referenced.y}\n "
                f"Z={self.referenced.z}\n "
                f"U={self.referenced.u}\n "
                f"V={self.referenced.v}\n "
                f"W={self.referenced.w}\n")

    async def reference(self):
        """Reference the hexapod."""
        self.referenced.x = 1
        self.referenced.y = 1
        self.referenced.z = 1
        self.referenced.u = 1
        self.referenced.v = 1
        self.referenced.w = 1

    async def format_target_position(self):
        """Return formatted string for target position"""
        return (f"X={self.target.x}\n "
                f"Y={self.target.y}\n "
                f"Z={self.target.z}\n "
                f"U={self.target.u}\n "
                f"V={self.target.v}\n "
                f"W={self.target.w}\n")

    async def set_low_position_soft_Limit(self, x, y, z, u, v, w):
        """Set the lower position software limit."""
        self.minimum_limit_x = x
        self.minimum_limit_y = y
        self.minimum_limit_z = z
        self.minimum_limit_u = u
        self.minimum_limit_v = v
        self.minimum_limit_w = w

    async def format_low_position_soft_limit(self):
        """Return formatted lower position software limit string."""
        return (f"X={self.minimum_limit_x}\n "
                f"Y={self.minimum_limit_y}\n "
                f"Z={self.minimum_limit_z}\n "
                f"U={self.minimum_limit_u}\n "
                f"V={self.minimum_limit_v}\n "
                f"W={self.minimum_limit_w}\n")

    async def set_high_position_soft_limit(self, x, y, z, u, v, w):
        """Set higher position software limit."""
        self.maximum_limit_x = x
        self.maximum_limit_y = y
        self.maximum_limit_z = z
        self.maximum_limit_u = u
        self.maximum_limit_v = v
        self.maximum_limit_w = w

    async def format_high_position_soft_limit(self):
        """Return formatted higher position software limit string."""
        return (f"X={self.maximum_limit_x}\n "
                f"Y={self.maximum_limit_y}\n "
                f"Z={self.maximum_limit_z}\n "
                f"U={self.maximum_limit_u}\n "
                f"V={self.maximum_limit_v}\n "
                f"W={self.maximum_limit_w}\n")

    async def format_on_target(self):
        """Return formatted on target string.

        Not implemented.
        """
        pass

    async def format_position_unit(self):
        """Return formatted get position unit string."""
        pass

    async def format_offset(self, x, y, z, u, v, w):
        """Set offset for hexapod."""
        self.log.debug("Setting offset.")
        await self.set_position(x=self.x+float(x), y=self.y+float(y), z=self.z+float(z),
                                u=self.u+float(u), v=self.v+float(v), w=self.w+float(w))

    async def check_offset(self, x, y, z, u, v, w):
        """Check that the hexapod can move."""
        return (f"X=1\n Y=1\n Z=1\n U=1\n V=1\n W=1\n")

    async def set_pivot_point(self, x, y, z):
        """Set the pivot point."""
        self.pivot.x = x
        self.pivot.y = y
        self.pivot.z = z

    async def format_pivot_point(self):
        """Return formatted get pivot point string"""
        return f"R={self.pivot.x}\n S={self.pivot.y}\n T={self.pivot.z}\n"

    async def format_check_active_soft_limit(self):
        """Check that the software limits are active."""
        pass

    async def activate_soft_limit(self, x, y, z, u, v, w):
        """Activate the software limits."""
        pass

    async def set_clv(self, x, y, z, u, v, w):
        """Set the closed loop velocity."""
        pass

    async def format_clv(self):
        """Return the closed loop velocity."""
        pass

    async def set_sv(self, velocity):
        """Set the system velocity."""
        self.sv = velocity

    async def format_sv(self):
        """Return the system velocity."""
        return f"{self.sv}\n"

    async def format_error(self):
        """Return get error string"""
        return "0\n"
