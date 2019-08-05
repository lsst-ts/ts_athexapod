import asyncio

from lsst.ts import salobj
import SALPY_Test
import random

# send a Test scalars event with int0=1
# wait 0.5 seconds
# flush the read buffer and wait for an event
# wait 0.5 more seconds *while waiting to receive)
# send another Test scalars event with int0=2
# check that the event read is the 2nd one, not the first one

print("create remote")
remote = salobj.Remote(SALPY_Test, index=1)
print("create controller")
controller = salobj.Controller(SALPY_Test, index=1)


def putScalar(scalar):
    data = controller.evt_scalars.DataType()
    data.int0 = scalar
    print(f"put scalars event with int0={data.int0}")
    controller.evt_scalars.put(data)


async def sendCmd_getMsg():
    remote.evt_scalars.flush()
    await asyncio.sleep(5)
    task = remote.evt_scalars.next(flush=False, timeout=60)  # Gets a new scalars event
    cmd_start_data = remote.cmd_start.DataType()
    remote.cmd_start.start(cmd_start_data, wait_done=False)  # Publish a start command
    print("start waiting for evt_scalars")
    data = await task  # Wait until the event is received (or timeout)
    print(f"read scalars event with int0={data.int0}")
    return data


async def getCmd_sendMsg(x):
    await controller.cmd_start.next()  # Wait until it gets a start command
    print("Command received...")
    putScalar(x)  # Publish event with int0=x


async def doit():
    x = random.randint(0, 100)
    asyncio.ensure_future(getCmd_sendMsg(x))
    data = await sendCmd_getMsg()
    assert x == data.int0

asyncio.get_event_loop().run_until_complete(doit())
