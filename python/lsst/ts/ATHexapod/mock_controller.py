class MockController:
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
        self.reference_x = 0
        self.reference_y = 0
        self.reference_z = 0
        self.reference_u = 0
        self.reference_v = 0
        self.reference_w = 0
        self.sv = 0
        self.pivot_x = 0
        self.pivot_y = 0
        self.pivot_z = 0

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.connected = False

    async def real_position(self):
        return [self.x, self.y, self.z, self.u, self.v, self.w]

    async def motion_status(self):
        return tuple([0, 0, 0, 0, 0, 0])

    async def controller_ready(self):
        self.ready = True
        return self.ready

    async def stop_all_axes(self):
        pass

    async def set_position(self, x, y, z, u, v, w):
        self.x = x
        self.y = y
        self.z = z
        self.u = u
        self.v = v
        self.w = w

    async def referencing_result(self):
        return [self.reference_x, self.reference_y, self.reference_z, self.reference_u, self.reference_v,
                self.reference_w]

    async def reference(self):
        self.reference_x = 1
        self.reference_y = 1
        self.reference_z = 1
        self.reference_u = 1
        self.reference_v = 1
        self.reference_w = 1

    async def target_position(self):
        pass

    async def set_low_position_soft_Limit(self, x, y, z, u, v, w):
        pass

    async def get_low_position_soft_limit(self):
        pass

    async def set_high_position_soft_limit(self, x, y, z, u, v, w):
        pass

    async def get_high_position_soft_limit(self):
        pass

    async def on_target(self):
        pass

    async def get_position_unit(self):
        pass

    async def offset(self, x, y, z, u, v, w):
        pass

    async def check_offset(self, x, y, z, u, v, w):
        pass

    async def set_pivot_point(self, x, y, z):
        self.pivot_x = x
        self.pivot_y = y
        self.pivot_z = z

    async def getPivotPoint(self):
        return [self.pivot_x, self.pivot_y, self.pivot_z]

    async def check_active_soft_limit(self):
        pass

    async def activate_soft_limit(self, x, y, z, u, v, w):
        pass

    async def set_clv(self, x, y, z, u, v, w):
        pass

    async def get_clv(self):
        pass

    async def set_sv(self, velocity):
        self.sv = velocity

    async def get_sv(self):
        return self.sv

    async def get_error(self):
        pass
