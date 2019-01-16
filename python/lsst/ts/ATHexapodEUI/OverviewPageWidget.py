
import QTHelpers
from lsst.ts.ATHexapodEUI.ATHexapodEnumerations import SummaryStates
from lsst.ts.ATHexapodEUI.DataCache import DataCache
from pyqtgraph.Qt import QtGui


class OverviewPageWidget(QtGui.QWidget):
    def __init__(self, ATHexapod):
        QtGui.QWidget.__init__(self)
        self.ATHexapod = ATHexapod
        self.layout = QtGui.QVBoxLayout()
        self.dataLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.dataLayout)
        self.setLayout(self.layout)

        self.row = 0
        self.col = 0
        # self.summaryStateLabel = QtGui.QLabel("UNKNOWN")
        # self.dataLayout.addWidget(QtGui.QLabel("Summary State"), self.row, self.col)
        # self.dataLayout.addWidget(self.summaryStateLabel, self.row, self.col + 1)

        self.dataEventSummaryState = DataCache()

        self.addInPosition()
        self.addPivot()
        self.addPositionLimits()
        self.addPositionUpdate()
        self.addTcpSettingsApplied()
        self.addVelocityLimits()
        self.addreadyForCommand()
        self.addAppliedSettingsMatchStart()
        self.ATHexapod.subscribeEvent_inPosition(self.processEventInPosition)
        self.ATHexapod.subscribeEvent_settingsAppliedPositionLimits(self.processEventSettingsAppliedPstnLmts)
        self.ATHexapod.subscribeEvent_settingsAppliedVelocities(self.processEventSettingsAppliedVelocities)
        self.ATHexapod.subscribeEvent_settingsAppliedPivot(self.processEventSettingsAppliedPivot)
        self.ATHexapod.subscribeEvent_positionUpdate(self.processEventPositionUpdate)
        self.ATHexapod.subscribeEvent_settingsAppliedTcp(self.processEventSettingsAppliedTcp)
        self.ATHexapod.subscribeEvent_readyForCommand(self.processEventReadyForCommand)
        self.ATHexapod.subscribeEvent_appliedSettingsMatchStart(self.processEventAppliedSettingsMatchStart)

    def addAppliedSettingsMatchStart(self):
        self.AppliedSettingsMatchStart = QtGui.QLineEdit()
        self.AppliedSettingsMatchStart.setReadOnly(True)

        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("AppliedSettingsMatchStart"), self.row, col)
        self.dataLayout.addWidget(self.AppliedSettingsMatchStart, self.row + 1, col)
        self.row += 2

    def addInPosition(self):
        self.InPosition = QtGui.QLineEdit()
        self.InPosition.setReadOnly(True)

        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("InPosition"), self.row, col)
        self.dataLayout.addWidget(self.InPosition, self.row + 1, col)
        self.row += 2

    def addPositionLimits(self):
        self.limitXYMax = QtGui.QLineEdit()
        self.limitXYMax.setReadOnly(True)
        self.limitZMin = QtGui.QLineEdit()
        self.limitZMin.setReadOnly(True)
        self.limitZMax = QtGui.QLineEdit()
        self.limitZMax.setReadOnly(True)
        self.limitUVMax = QtGui.QLineEdit()
        self.limitUVMax.setReadOnly(True)
        self.limitWMin = QtGui.QLineEdit()
        self.limitWMin.setReadOnly(True)
        self.limitWMax = QtGui.QLineEdit()
        self.limitWMax.setReadOnly(True)

        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("limitXYMax"), self.row, col)
        self.dataLayout.addWidget(self.limitXYMax, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("limitZMin"), self.row, col)
        self.dataLayout.addWidget(self.limitZMin, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("limitZMax"), self.row, col)
        self.dataLayout.addWidget(self.limitZMax, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("limitUVMax"), self.row, col)
        self.dataLayout.addWidget(self.limitUVMax, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("limitWMin"), self.row, col)
        self.dataLayout.addWidget(self.limitWMin, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("limitWMax"), self.row, col)
        self.dataLayout.addWidget(self.limitWMax, self.row + 1, col)
        self.row += 2

    def addVelocityLimits(self):
        self.velocityXYMax = QtGui.QLineEdit()
        self.velocityXYMax.setReadOnly(True)
        self.velocityRxRyMax = QtGui.QLineEdit()
        self.velocityRxRyMax.setReadOnly(True)
        self.velocityZMax = QtGui.QLineEdit()
        self.velocityZMax.setReadOnly(True)
        self.velocityRzMax = QtGui.QLineEdit()
        self.velocityRzMax.setReadOnly(True)

        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("velocityXYMax"), self.row, col)
        self.dataLayout.addWidget(self.velocityXYMax, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("velocityRxRyMax"), self.row, col)
        self.dataLayout.addWidget(self.velocityRxRyMax, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("velocityZMax"), self.row, col)
        self.dataLayout.addWidget(self.velocityZMax, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("velocityRzMax"), self.row, col)
        self.dataLayout.addWidget(self.velocityRzMax, self.row + 1, col)
        self.row += 2

    def addPivot(self):
        self.pivotX = QtGui.QLineEdit()
        self.pivotX.setReadOnly(True)
        self.pivotY = QtGui.QLineEdit()
        self.pivotY.setReadOnly(True)
        self.pivotZ = QtGui.QLineEdit()
        self.pivotZ.setReadOnly(True)

        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("pivotX"), self.row, col)
        self.dataLayout.addWidget(self.pivotX, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("pivotY"), self.row, col)
        self.dataLayout.addWidget(self.pivotY, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("pivotZ"), self.row, col)
        self.dataLayout.addWidget(self.pivotZ, self.row + 1, col)
        self.row += 2

    def addPositionUpdate(self):
        self.positionX = QtGui.QLineEdit()
        self.positionX.setReadOnly(True)
        self.positionY = QtGui.QLineEdit()
        self.positionY.setReadOnly(True)
        self.positionZ = QtGui.QLineEdit()
        self.positionZ.setReadOnly(True)
        self.positionU = QtGui.QLineEdit()
        self.positionU.setReadOnly(True)
        self.positionV = QtGui.QLineEdit()
        self.positionV.setReadOnly(True)
        self.positionW = QtGui.QLineEdit()
        self.positionW.setReadOnly(True)

        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("positionX"), self.row, col)
        self.dataLayout.addWidget(self.positionX, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("positionY"), self.row, col)
        self.dataLayout.addWidget(self.positionY, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("positionZ"), self.row, col)
        self.dataLayout.addWidget(self.positionZ, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("positionU"), self.row, col)
        self.dataLayout.addWidget(self.positionU, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("positionV"), self.row, col)
        self.dataLayout.addWidget(self.positionV, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("positionW"), self.row, col)
        self.dataLayout.addWidget(self.positionW, self.row + 1, col)
        self.row += 2

    def addTcpSettingsApplied(self):
        self.ip = QtGui.QLineEdit()
        self.ip.setReadOnly(True)
        self.port = QtGui.QLineEdit()
        self.port.setReadOnly(True)
        self.readTimeout = QtGui.QLineEdit()
        self.readTimeout.setReadOnly(True)
        self.writeTimeout = QtGui.QLineEdit()
        self.writeTimeout.setReadOnly(True)
        self.connectionTimeout = QtGui.QLineEdit()
        self.connectionTimeout.setReadOnly(True)
        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("ip"), self.row, col)
        self.dataLayout.addWidget(self.ip, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("port"), self.row, col)
        self.dataLayout.addWidget(self.port, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("readTimeout"), self.row, col)
        self.dataLayout.addWidget(self.readTimeout, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("writeTimeout"), self.row, col)
        self.dataLayout.addWidget(self.writeTimeout, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("connectionTimeout"), self.row, col)
        self.dataLayout.addWidget(self.connectionTimeout, self.row + 1, col)
        self.row += 2

    def addreadyForCommand(self):
        self.readyForCommand = QtGui.QLineEdit()
        self.readyForCommand.setReadOnly(True)
        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("readyForCommand"), self.row, col)
        self.dataLayout.addWidget(self.readyForCommand, self.row + 1, col)
        self.row += 2

    def setPageActive(self, active):
        self.pageActive = active
        if self.pageActive:
            self.updatePage()

    def updatePage(self):
        if not self.pageActive:
            return

        # if self.dataEventSummaryState.hasBeenUpdated():
        #     data = self.dataEventSummaryState.get()
        #     state = data.summaryState
        #     summaryStateText = "UNKNOWN"
        #     if state == SummaryStates.OfflineState:
        #         summaryStateText = "Offline"
        #     elif state == SummaryStates.DisabledState:
        #         summaryStateText = "Disabled"
        #     elif state == SummaryStates.EnabledState:
        #         summaryStateText = "Enabled"
        #     elif state == SummaryStates.FaultState:
        #         summaryStateText = "Fault"
        #     self.summaryStateLabel.setText(summaryStateText)

    def processEventSummaryState(self, data):
        self.dataEventSummaryState.set(data[-1])

    def processEventAppliedSettingsMatchStart(self, data):
        if data[-1].appliedSettingsMatchStartIsTrue:
            self.AppliedSettingsMatchStart.setText("True")
        else:
            self.AppliedSettingsMatchStart.setText("False")

    def processEventInPosition(self, data):
        if data[-1].inPosition:
            self.InPosition.setText("True")
        else:
            self.InPosition.setText("False")

    def processEventSettingsAppliedPstnLmts(self, data):
        limitXYMax = data[-1].limitXYMax
        limitZMin = data[-1].limitZMin
        limitZMax = data[-1].limitZMax
        limitUVMax = data[-1].limitUVMax
        limitWMin = data[-1].limitWMin
        limitWMax = data[-1].limitWMax
        self.limitXYMax.setText(str(limitXYMax))
        self.limitZMin.setText(str(limitZMin))
        self.limitZMax.setText(str(limitZMax))
        self.limitUVMax.setText(str(limitUVMax))
        self.limitWMin.setText(str(limitWMin))
        self.limitWMax.setText(str(limitWMax))

    def processEventSettingsAppliedVelocities(self, data):
        velocityXYMax = data[-1].velocityXYMax
        velocityRxRyMax = data[-1].velocityRxRyMax
        velocityZMax = data[-1].velocityZMax
        velocityRzMax = data[-1].velocityRzMax
        self.velocityXYMax.setText(str(velocityXYMax))
        self.velocityRxRyMax.setText(str(velocityRxRyMax))
        self.velocityZMax.setText(str(velocityZMax))
        self.velocityRzMax.setText(str(velocityRzMax))

    def processEventSettingsAppliedPivot(self, data):
        pivotX = data[-1].pivotX
        pivotY = data[-1].pivotY
        pivotZ = data[-1].pivotZ
        self.pivotX.setText(str(pivotX))
        self.pivotY.setText(str(pivotY))
        self.pivotZ.setText(str(pivotZ))

    def processEventPositionUpdate(self, data):
        positionX = data[-1].positionX
        positionY = data[-1].positionY
        positionZ = data[-1].positionZ
        positionU = data[-1].positionU
        positionV = data[-1].positionV
        positionW = data[-1].positionW
        self.positionX.setText(str(positionX))
        self.positionY.setText(str(positionY))
        self.positionZ.setText(str(positionZ))
        self.positionU.setText(str(positionU))
        self.positionV.setText(str(positionV))
        self.positionW.setText(str(positionW))

    def processEventSettingsAppliedTcp(self, data):
        ip = data[-1].ip
        port = data[-1].port
        readTimeout = data[-1].readTimeout
        writeTimeout = data[-1].writeTimeout
        connectionTimeout = data[-1].connectionTimeout
        self.ip.setText(str(ip))
        self.port.setText(str(port))
        self.readTimeout.setText(str(readTimeout))
        self.writeTimeout.setText(str(writeTimeout))
        self.connectionTimeout.setText(str(connectionTimeout))

    def processEventReadyForCommand(self, data):
        if data[-1].readyForCommand:
            self.setText(str("True"))
        else:
            self.setText(str("False"))
