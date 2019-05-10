import asyncio

from lsst.ts import salobj
import SALPY_ATHexapod
import random

# send a Test scalars event with int0=1
# wait 0.5 seconds
# flush the read buffer and wait for an event
# wait 0.5 more seconds *while waiting to receive)
# send another Test scalars event with int0=2
# check that the event read is the 2nd one, not the first one

print("create remote")
remote = salobj.Remote(SALPY_ATHexapod, index=None)
print("create controller")
controller = salobj.Controller(SALPY_ATHexapod, index=None)


async def send_event(x, y, z, u, v, w):
    #await asyncio.sleep(0.5)
    await controller.cmd_start.next()
    print("Command received...")
    data = remote.evt_positionUpdate.DataType()
    data.positionX = x
    data.positionY = y
    data.positionZ = z
    data.positionU = u
    data.positionV = v
    data.positionW = w
    print(f"event sent:")
    for prop in dir(data):
      if not prop.startswith('__'):
        print(prop, getattr(data, prop))
    controller.evt_positionUpdate.put(data)

async def send_event_rnd():
    #await asyncio.sleep(0.5)
    await controller.cmd_start.next()
    print("Command received...")
    data = remote.evt_positionUpdate.DataType()
    data.positionX = random.uniform(1, 10)
    data.positionY = random.uniform(1, 10)
    data.positionZ = random.uniform(1, 10)
    data.positionU = random.uniform(1, 10)
    data.positionV = random.uniform(1, 10)
    data.positionW = random.uniform(1, 10)
    print(f"event sent:")
    for prop in dir(data):
      if not prop.startswith('__'):
        print(prop, getattr(data, prop))
    controller.evt_positionUpdate.put(data)

async def sendCommand_getMessage():
    # await asyncio.sleep(0.1)
    task = remote.evt_positionUpdate.next(flush=True, timeout=60)
    cmd_start_data = remote.cmd_start.DataType()
    remote.cmd_start.start(cmd_start_data, wait_done=False)
    print("start waiting for positionUpdate")
    data = await task
    print(f"event received:")
    for prop in dir(data):
      if not prop.startswith('__'):
        print(prop, getattr(data, prop))

async def doit():
    asyncio.ensure_future(send_event_rnd())
    await sendCommand_getMessage()

asyncio.get_event_loop().run_until_complete(doit())
