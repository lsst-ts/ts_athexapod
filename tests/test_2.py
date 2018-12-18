from lsst.ts.ATHexapod.ATHexapodCommands import ATHexapodCommand
from lsst.ts.pythonCommunicator.TcpCommunicator import TcpClient

hexCmd = ATHexapodCommand()
tcpcon = TcpClient(address='139.229.136.151', port=50000, connectTimeout=2, readTimeout=2, sendTimeout=2,)
tcpcon.connect()
tcpcon.sendMessage(hexCmd.getPositionUnit())

Axis1, onTargetX = str(tcpcon.getMessage()).split("=")
Axis2, onTargetY = str(tcpcon.getMessage()).split("=")
Axis3, onTargetZ = str(tcpcon.getMessage()).split("=")
Axis4, onTargetU = str(tcpcon.getMessage()).split("=")
Axis5, onTargetV = str(tcpcon.getMessage()).split("=")
Axis6, onTargetW = str(tcpcon.getMessage()).split("=")
print(Axis2)
print(bool(int(onTargetX)))
tcpcon.disconnect()
