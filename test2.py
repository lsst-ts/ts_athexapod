from atHexapodController.ATHexapodCommands import ATHexapodCommand
from pythonCommunicator.TcpCommunicator import TcpClientEndChar

hexCmd = ATHexapodCommand()
tcpcon = TcpClientEndChar(address='139.229.136.151', port=50000, connectTimeout=2, readTimeout=2, sendTimeout=2,
                         endStr='\n', maxLength=1024)
tcpcon.connect()
tcpcon.sendMessage(hexCmd.getSoftLimitStatus()+'\n')

Axis1, onTargetX = str(tcpcon.getMessage()).split("=")
Axis2, onTargetY = str(tcpcon.getMessage()).split("=")
Axis3, onTargetZ = str(tcpcon.getMessage()).split("=")
Axis4, onTargetU = str(tcpcon.getMessage()).split("=")
Axis5, onTargetV = str(tcpcon.getMessage()).split("=")
Axis6, onTargetW = str(tcpcon.getMessage()).split("=")
print(Axis2)
print(bool(int(onTargetX)))
tcpcon.disconnect()