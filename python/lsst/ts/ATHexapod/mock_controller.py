import asyncio
import re
import logging


class MockServer:
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
        self.commanded_x = 0
        self.commanded_y = 0
        self.commanded_z = 0
        self.commanded_u = 0
        self.commanded_v = 0
        self.commanded_w = 0
        self.reference_x = 0
        self.reference_y = 0
        self.reference_z = 0
        self.reference_u = 0
        self.reference_v = 0
        self.reference_w = 0
        self.sv = 1
        self.pivot_x = 0.
        self.pivot_y = 0.
        self.pivot_z = 0.
        self.command_calls = {
            b"\3": self.real_position,
            b"\5": self.motion_status,
            b"\7": self.controller_ready,
            b"MOV": self.set_position,
            b"FRF?": self.referencing_result,
            b"FRF": self.reference,
            b"MOV?": self.target_position,
            b"ERR?": self.get_error,
            b"NLM": self.set_low_position_soft_Limit,
            b"NLM?": self.get_low_position_soft_limit,
            b"PLM": self.set_high_position_soft_limit,
            b"PLM?": self.get_high_position_soft_limit,
            b"SPI": self.set_pivot_point,
            b"SPI?": self.getPivotPoint,
            b"VLS": self.set_sv,
            b"VLS?": self.get_sv}
        self.commands = [
            re.compile(b"^(?P<cmd>\3)$"),
            re.compile(b"^(?P<cmd>\5)$"),
            re.compile(b"^(?P<cmd>\6)$"),
            re.compile(b"^(?P<cmd>\7)$"),
            re.compile((br"^(?P<cmd>MOV) (?P<x>X) (?P<x_value>\d+.\d+) "
                        br"(?P<y>Y) (?P<y_value>\d+.\d+) (?P<z>Z) (?P<z_value>\d+.\d+) "
                        br"(?P<u>U) (?P<u_value>\d+.\d+) (?P<v>V) (?P<v_value>\d+.\d+) "
                        br"(?P<w>W) (?P<w_value>\d+.\d+)$")),
            re.compile(br"^(?P<cmd>FRF\?)$"),
            re.compile(br"^(?P<cmd>FRF) X Y Z U V W$"),
            re.compile(br"^(?P<cmd>MOV\?) X Y Z U V W$"),
            re.compile(br"^(?P<cmd>ERR\?)$"),
            re.compile((br"^(?P<cmd>NLM) (?P<x>X) (?P<x_value>-\d+.\d+) (?P<y>Y) (?P<y_value>-\d+.\d+) "
                        br"(?P<z>Z) (?P<z_value>-\d+.\d+) (?P<u>U) (?P<u_value>-\d+.\d+) "
                        br"(?P<v>V) (?P<v_value>-\d+.\d+) (?P<w>W) (?P<w_value>-\d+.\d+)$")),
            re.compile(rb"^(?P<cmd>NLM\?) X Y Z U V W$"),
            re.compile((br"^(?P<cmd>PLM) (?P<x>X) (?P<x_value>\d+.\d+) (?P<y>Y) (?P<y_value>\d+.\d+)"
                        br"(?P<z>Z) (?P<z_value>\d+.\d+) (?P<u>U) (?P<u_value>\d+.\d+)"
                        br"(?P<v>V) (?P<v_value>\d+.\d+) (?P<w>W) (?P<w_value>\d+.\d+)$")),
            re.compile(br"^(?P<cmd>PLM\?) X Y Z U V W$"),
            re.compile((br"^(?P<cmd>SPI) (?P<x>X) (?P<x_value>\d+.\d+) "
                        br"(?P<y>Y) (?P<y_value>\d+.\d+) (?P<z>Z) (?P<z_value>\d+.\d+)$")),
            re.compile(br"^(?P<cmd>SPI\?)$"),
            re.compile(br"^(?P<cmd>VLS) (?P<velocity>\d+.\d+)$"),
            re.compile(br"^(?P<cmd>VLS\?)$")]
        self.log = logging.getLogger(__name__)

    async def start(self):
        self.log.debug("Starting Server")
        self.server = await asyncio.start_server(client_connected_cb=self.cmd_loop,
                                                 host=self.host,
                                                 port=self.port)
        self.log.debug("Server started")

    async def stop(self):
        self.log.debug("Closing server")
        self.server.close()
        await asyncio.wait_for(self.server.wait_closed(), timeout=5)
        self.log.debug("Server closed")

    async def cmd_loop(self, reader, writer):
        while True:
            line = await reader.readline()
            self.log.debug(f"Received: {line}")
            if not line:
                writer.close()
                return
            # line = line.decode()
            self.log.debug(f"Decoded line: {line}")
            for command in self.commands:
                matched_command = command.match(line)
                if matched_command:
                    self.log.debug(f"Matched command {line}")
                    if matched_command.group('cmd') in self.command_calls:
                        called_command = self.command_calls[matched_command.group('cmd')]
                        self.log.debug(f"cmd group:{matched_command.group('cmd')}")
                        if matched_command.group('cmd') in [b'NLM', b'MOV', b'PLM']:
                            self.log.debug(f"Grabbing command {matched_command.group('cmd')}")
                            await called_command(x=matched_command.group('x_value'),
                                                 y=matched_command.group('y_value'),
                                                 z=matched_command.group('z_value'),
                                                 u=matched_command.group('u_value'),
                                                 v=matched_command.group('v_value'),
                                                 w=matched_command.group('w_value'))
                        elif matched_command.group('cmd') in [b'SPI']:
                            self.log.debug(f"Grabbing command {matched_command.group('cmd')}")
                            await called_command(x=matched_command.group('x_value'),
                                                 y=matched_command.group('y_value'),
                                                 z=matched_command.group('z_value'))
                        elif matched_command.group('cmd') in [b'VLS']:
                            self.log.debug(f"Grabbing command {matched_command.group('cmd')}")
                            await called_command(velocity=matched_command.group('velocity'))
                        elif await called_command() is not None:
                            self.log.debug(f"Sent {await called_command()}")
                            writer.write(await called_command())
                            await writer.drain()
                    else:
                        raise Exception(f"{matched_command.group('cmd')} is not implemented.")

    async def real_position(self):
        return f"X={self.x} Y={self.y} Z={self.z} U={self.u} V={self.v} W={self.w}\n".encode()

    async def motion_status(self):
        return f"0\n".encode()

    async def controller_ready(self):
        self.ready = True
        return f"{chr(177)}\n".encode()

    async def stop_all_axes(self):
        pass

    async def set_position(self, x, y, z, u, v, w):
        self.log.debug("Setting position")
        self.commanded_x = x.decode()
        self.comanded_y = y.decode()
        self.commanded_z = z.decode()
        self.commanded_u = u.decode()
        self.commanded_v = v.decode()
        self.commanded_w = w.decode()
        self.x = x.decode()
        self.y = y.decode()
        self.z = z.decode()
        self.u = u.decode()
        self.v = v.decode()
        self.w = w.decode()

    async def referencing_result(self):
        return (f"X={self.reference_x} "
                f"Y={self.reference_y} "
                f"Z={self.reference_z} "
                f"U={self.reference_u} "
                f"V={self.reference_v} "
                f"W={self.reference_w}\n".encode())

    async def reference(self):
        self.reference_x = 1
        self.reference_y = 1
        self.reference_z = 1
        self.reference_u = 1
        self.reference_v = 1
        self.reference_w = 1

    async def target_position(self):
        return (f"X={self.commanded_x} "
                f"Y={self.commanded_y} "
                f"Z={self.commanded_z} "
                f"U={self.commanded_u} "
                f"V={self.commanded_v} "
                f"W={self.commanded_w}\n".encode())

    async def set_low_position_soft_Limit(self, x, y, z, u, v, w):
        self.minimum_limit_x = x.decode()
        self.minimum_limit_y = y.decode()
        self.minimum_limit_z = z.decode()
        self.minimum_limit_u = u.decode()
        self.minimum_limit_v = v.decode()
        self.minimum_limit_w = w.decode()

    async def get_low_position_soft_limit(self):
        return (f"X={self.minimum_limit_x} " 
                f"Y={self.minimum_limit_y} "
                f"Z={self.minimum_limit_z} "
                f"U={self.minimum_limit_u} "
                f"V={self.minimum_limit_v} "
                f"W={self.minimum_limit_w}\n".encode())

    async def set_high_position_soft_limit(self, x, y, z, u, v, w):
        self.maximum_limit_x = x.decode()
        self.maximum_limit_y = y.decode()
        self.maximum_limit_z = z.decode()
        self.maximum_limit_u = u.decode()
        self.maximum_limit_v = v.decode()
        self.maximum_limit_w = w.decode()

    async def get_high_position_soft_limit(self):
        return (f"X={self.maximum_limit_x} "
                f"Y={self.maximum_limit_y} "
                f"Z={self.maximum_limit_z} "
                f"U={self.maximum_limit_u} "
                f"V={self.maximum_limit_v} "
                f"W={self.maximum_limit_w}\n".encode())

    async def on_target(self):
        pass

    async def get_position_unit(self):
        pass

    async def offset(self, x, y, z, u, v, w):
        pass

    async def check_offset(self, x, y, z, u, v, w):
        pass

    async def set_pivot_point(self, x, y, z):
        self.pivot_x = x.decode()
        self.pivot_y = y.decode()
        self.pivot_z = z.decode()

    async def getPivotPoint(self):
        return f"R={self.pivot_x} S={self.pivot_y} T={self.pivot_z}\n".encode()

    async def check_active_soft_limit(self):
        pass

    async def activate_soft_limit(self, x, y, z, u, v, w):
        pass

    async def set_clv(self, x, y, z, u, v, w):
        pass

    async def get_clv(self):
        pass

    async def set_sv(self, velocity):
        self.sv = velocity.decode()

    async def get_sv(self):
        return f"{self.sv}\n".encode()

    async def get_error(self):
        return "0\n".encode()
