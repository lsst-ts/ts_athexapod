from atHexapodController.ATHexapodCommands import ATHexapodCommand
from pythonCommunicator.TcpCommunicator import TcpClienEndChar
import time
import unittest

class TestAtHexapod(inittest.TestCase):

	def setUp(self):
		hexCmd = ATHexapodCommand()
		tcpcon = TcpClienEndChar(address='139.229.136.151', port=50000, connectTimeout=2, readTimeout=2, sendTimeout=2, endStr='\n', maxLength = 1024)
		tcpcon.connect()

	if(True):
		#tcpcon.sendMessage(hexCmd.setTargetPosition(X=1, Y=1, Z=1, U=0, V=0, W=0)+"\n")
		#Need to initialize first!
		print("Request status")
		tcpcon.sendMessage('\3\n')
		for i in range(6):
			tcpcon.getMessage()
		time.sleep(1)

	if(False):
		tcpcon.sendMessage(hexCmd.getRealPosition()+'\n')
		for i in range(6):
			tcpcon.getMessage()
		time.sleep(1)

		tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
		tcpcon.getMessage()
		time.sleep(1)

		tcpcon.sendMessage(hexCmd.requestControllerReadyStatus()+"\n")
		tcpcon.getMessage()
		time.sleep(1)

		tcpcon.sendMessage(hexCmd.getLowPositionSoftLimit()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		time.sleep(1)

		tcpcon.sendMessage(hexCmd.getOnTargetState()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		time.sleep(1)

		tcpcon.sendMessage(hexCmd.getHighPositionSoftLimit()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		time.sleep(1)

		tcpcon.sendMessage(hexCmd.getPositionUnit()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		time.sleep(1)

	if(False):
		print("Stop all axes without motion happening")
		tcpcon.command(hexCmd.stopAllAxes()+"\n")
		time.sleep(1)

	if(False):
		print("Try to move all axis")
		tcpcon.sendMessage(hexCmd.setTargetPosition(X=3, Y=3, Z=3, U=0, V=0, W=0)+"\n")
		for i in range(60):
			tcpcon.sendMessage(hexCmd.getRealPosition()+'\n')
			for i in range(6):
				tcpcon.getMessage()
			time.sleep(1)

	if(False):
		print("Try to move a few axis")
		tcpcon.sendMessage(hexCmd.setTargetPosition(Y=3, Z=3)+"\n")
		for i in range(60):
			tcpcon.sendMessage(hexCmd.getRealPosition()+'\n')
			for i in range(6):
				tcpcon.getMessage()
			time.sleep(1)

	if(False):
		print("Try to move and stop")
		tcpcon.sendMessage(hexCmd.setTargetPosition(X=3, Y=3, Z=3)+"\n")
		for i in range(3):
			tcpcon.sendMessage(hexCmd.getRealPosition()+'\n')
			for i in range(6):
				tcpcon.getMessage()
			time.sleep(1)
		tcpcon.sendMessage(hexCmd.stopAllAxes()+"\n")
		for i in range(18):
			tcpcon.sendMessage(hexCmd.getRealPosition()+'\n')
			for i in range(6):
				tcpcon.getMessage()
			time.sleep(1)

	if(False):
		print("Try executing commands when the hexapod is in motion")
		tcpcon.sendMessage(hexCmd.setTargetPosition(X=3, Y=3, Z=3, U=3, V=3, W=3)+"\n")
		tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
		tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.setTargetPosition(X=0, Y=0, Z=0, U=0, V=0, W=0)+"\n")
		for i in range(60):
			tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
			for i in range(6):
				tcpcon.getMessage()
			tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
			tcpcon.getMessage()
			time.sleep(1)
		time.sleep(10)

	if(False):
		print("Update relative position")
		tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.setTargetRelativeToCurrentPosition(X=0.1, Y=0.2, Z=0.2, U=0.2, V=0.3, W=0.3)+"\n")
		for i in range(10):
			tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
			for i in range(6):
				tcpcon.getMessage()
			tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
			tcpcon.getMessage()
			time.sleep(1)
		tcpcon.sendMessage(hexCmd.setTargetRelativeToCurrentPosition(X=0.1, Y=0.1, Z=0.1, U=0.1, V=0.1, W=0.1)+"\n")
		for i in range(10):
			tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
			for i in range(6):
				tcpcon.getMessage()
			tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
			tcpcon.getMessage()
			time.sleep(1)
		tcpcon.sendMessage(hexCmd.setTargetRelativeToCurrentPosition(X=0.1, Y=0.1, Z=0.1, U=0.1, V=0.1, W=0.1)+"\n")
		for i in range(10):
			tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
			for i in range(6):
				tcpcon.getMessage()
			tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
			tcpcon.getMessage()
			time.sleep(1)
		tcpcon.sendMessage(hexCmd.setTargetRelativeToCurrentPosition(X=0.1, Y=0.1, Z=0.1, U=0.1, V=0.1, W=0.1)+"\n")
		for i in range(10):
			tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
			for i in range(6):
				tcpcon.getMessage()
			tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
			tcpcon.getMessage()
			time.sleep(1)

	if(False):
		print("Set and request limits")
		tcpcon.sendMessage(hexCmd.getLowPositionSoftLimit()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.setLowPositionSoftLimit(X=-22.5, Y=-22.5, Z=-12.5, U=-7.5, V=-7.5, W=-12.5)+"\n")
		tcpcon.sendMessage(hexCmd.getLowPositionSoftLimit()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		time.sleep(1)

		tcpcon.sendMessage(hexCmd.getHighPositionSoftLimit()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.setHighPositionSoftLimit(X=22.5, Y=22.5, Z=12.5, U=7.5, V=7.5, W=12.5)+"\n")
		tcpcon.sendMessage(hexCmd.getHighPositionSoftLimit()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		time.sleep(1)

	if(False):
		print("Get error number")
		tcpcon.sendMessage(hexCmd.getErrorNumber()+"\n")
		tcpcon.getMessage()

	if(True):
		print("Update Pivot")
		tcpcon.sendMessage(hexCmd.getPivotPoint()+"\n")
		tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
		tcpcon.getMessage()
		for i in range(3):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.setPivotPoint(X=2, Y=2, Z=2)+"\n")
		tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
		tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.getPivotPoint()+"\n")
		for i in range(3):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.getPivotPoint()+"\n")
		tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
		tcpcon.getMessage()
		for i in range(3):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.setPivotPoint(X=0, Y=0, Z=0)+"\n")
		tcpcon.sendMessage(hexCmd.getRealPosition()+"\n")
		for i in range(6):
			tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.requestMotionStatus()+"\n")
		tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.getPivotPoint()+"\n")
		for i in range(3):
			tcpcon.getMessage()

	if(False):
		print("test virtual move")
		tcpcon.sendMessage(hexCmd.virtualMove(X=22.5, Y=22.5, Z=12.5, U=7.5, V=7.5, W=12.5)+"\n")
		tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.virtualMove(X=26.5, Y=26.5, Z=12.5, U=7.5, V=7.5, W=12.5)+"\n")
		tcpcon.getMessage()
		tcpcon.sendMessage(hexCmd.virtualMove(X=0.5, Y=0.5, Z=0.5, U=0.5, V=0.5, W=0.5)+"\n")
		tcpcon.getMessage()

	tcpcon.disconnect()
