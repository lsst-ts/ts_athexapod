from pythonCommunicator.TcpCommunicator import TcpServerEndChar
import time

server = TcpServerEndChar(address='localhost', port=50000, connectTimeout=600, readTimeout=10, sendTimeout=2, endStr="\n", maxLength = 1024)
server.connect()
try:
	message = server.getMessage()	
	server.sendMessage("X=1 Y=2 Z=4 U=2 V=2 W=4\n")
except Exception as e:
	print(e)
time.sleep(1)
server.disconnect()
print("End...")
