
from lsst.ts.ATHexapodEUI import QTHelpers
from lsst.ts.ATHexapodEUI.ATHexapodEnumerations import SummaryStates
from lsst.ts.ATHexapodEUI.DataCache import DataCache
from pyqtgraph.Qt import QtGui


class PositionPageWidget(QtGui.QWidget):
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

        self.addPositionTelemetry()
        self.ATHexapod.subscribeTelemetry_positionStatus(self.processEventPositionUpdate)

    def addPositionTelemetry(self):
        self.setpointPositionX = QtGui.QLineEdit()
        self.setpointPositionX.setReadOnly(True)
        self.setpointPositionY = QtGui.QLineEdit()
        self.setpointPositionY.setReadOnly(True)
        self.setpointPositionZ = QtGui.QLineEdit()
        self.setpointPositionZ.setReadOnly(True)
        self.setpointPositionU = QtGui.QLineEdit()
        self.setpointPositionU.setReadOnly(True)
        self.setpointPositionV = QtGui.QLineEdit()
        self.setpointPositionV.setReadOnly(True)
        self.setpointPositionW = QtGui.QLineEdit()
        self.setpointPositionW.setReadOnly(True)

        self.reportedPositionX = QtGui.QLineEdit()
        self.reportedPositionX.setReadOnly(True)
        self.reportedPositionY = QtGui.QLineEdit()
        self.reportedPositionY.setReadOnly(True)
        self.reportedPositionZ = QtGui.QLineEdit()
        self.reportedPositionZ.setReadOnly(True)
        self.reportedPositionU = QtGui.QLineEdit()
        self.reportedPositionU.setReadOnly(True)
        self.reportedPositionV = QtGui.QLineEdit()
        self.reportedPositionV.setReadOnly(True)
        self.reportedPositionW = QtGui.QLineEdit()
        self.reportedPositionW.setReadOnly(True)

        self.positionFollowingErrorX = QtGui.QLineEdit()
        self.positionFollowingErrorX.setReadOnly(True)
        self.positionFollowingErrorY = QtGui.QLineEdit()
        self.positionFollowingErrorY.setReadOnly(True)
        self.positionFollowingErrorZ = QtGui.QLineEdit()
        self.positionFollowingErrorZ.setReadOnly(True)
        self.positionFollowingErrorU = QtGui.QLineEdit()
        self.positionFollowingErrorU.setReadOnly(True)
        self.positionFollowingErrorV = QtGui.QLineEdit()
        self.positionFollowingErrorV.setReadOnly(True)
        self.positionFollowingErrorW = QtGui.QLineEdit()
        self.positionFollowingErrorW.setReadOnly(True)

        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("positionFollowingErrorX"), self.row, col)
        self.dataLayout.addWidget(self.positionFollowingErrorX, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("positionFollowingErrorY"), self.row, col)
        self.dataLayout.addWidget(self.positionFollowingErrorY, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("positionFollowingErrorZ"), self.row, col)
        self.dataLayout.addWidget(self.positionFollowingErrorZ, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("positionFollowingErrorU"), self.row, col)
        self.dataLayout.addWidget(self.positionFollowingErrorU, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("positionFollowingErrorV"), self.row, col)
        self.dataLayout.addWidget(self.positionFollowingErrorV, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("positionFollowingErrorW"), self.row, col)
        self.dataLayout.addWidget(self.positionFollowingErrorW, self.row + 1, col)
        self.row += 2

        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("reportedPositionX"), self.row, col)
        self.dataLayout.addWidget(self.reportedPositionX, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("reportedPositionY"), self.row, col)
        self.dataLayout.addWidget(self.reportedPositionY, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("reportedPositionZ"), self.row, col)
        self.dataLayout.addWidget(self.reportedPositionZ, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("reportedPositionU"), self.row, col)
        self.dataLayout.addWidget(self.reportedPositionU, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("reportedPositionV"), self.row, col)
        self.dataLayout.addWidget(self.reportedPositionV, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("reportedPositionW"), self.row, col)
        self.dataLayout.addWidget(self.reportedPositionW, self.row + 1, col)
        self.row += 2

        col = self.col
        self.dataLayout.addWidget(QtGui.QLabel("setpointPositionX"), self.row, col)
        self.dataLayout.addWidget(self.setpointPositionX, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("setpointPositionY"), self.row, col)
        self.dataLayout.addWidget(self.setpointPositionY, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("setpointPositionZ"), self.row, col)
        self.dataLayout.addWidget(self.setpointPositionZ, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("setpointPositionU"), self.row, col)
        self.dataLayout.addWidget(self.setpointPositionU, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("setpointPositionV"), self.row, col)
        self.dataLayout.addWidget(self.setpointPositionV, self.row + 1, col)
        col += 1
        self.dataLayout.addWidget(QtGui.QLabel("setpointPositionW"), self.row, col)
        self.dataLayout.addWidget(self.setpointPositionW, self.row + 1, col)

    def setPageActive(self, active):
        self.pageActive = active
        if self.pageActive:
            self.updatePage()

    def updatePage(self):
        if not self.pageActive:
            return

    def processEventPositionUpdate(self, data):
        setpointPositionX = data[-1].setpointPosition[0]
        setpointPositionY = data[-1].setpointPosition[1]
        setpointPositionZ = data[-1].setpointPosition[2]
        setpointPositionU = data[-1].setpointPosition[3]
        setpointPositionV = data[-1].setpointPosition[4]
        setpointPositionW = data[-1].setpointPosition[5]

        reportedPositionX = data[-1].reportedPosition[0]
        reportedPositionY = data[-1].reportedPosition[1]
        reportedPositionZ = data[-1].reportedPosition[2]
        reportedPositionU = data[-1].reportedPosition[3]
        reportedPositionV = data[-1].reportedPosition[4]
        reportedPositionW = data[-1].reportedPosition[5]

        positionFollowingErrorX = data[-1].positionFollowingError[0]
        positionFollowingErrorY = data[-1].positionFollowingError[1]
        positionFollowingErrorZ = data[-1].positionFollowingError[2]
        positionFollowingErrorU = data[-1].positionFollowingError[3]
        positionFollowingErrorV = data[-1].positionFollowingError[4]
        positionFollowingErrorW = data[-1].positionFollowingError[5]

        self.setpointPositionX.setText("{:.5f}".format(setpointPositionX))
        self.setpointPositionY.setText("{:.5f}".format(setpointPositionY))
        self.setpointPositionZ.setText("{:.5f}".format(setpointPositionZ))
        self.setpointPositionU.setText("{:.5f}".format(setpointPositionU))
        self.setpointPositionV.setText("{:.5f}".format(setpointPositionV))
        self.setpointPositionW.setText("{:.5f}".format(setpointPositionW))

        self.reportedPositionX.setText("{:.5f}".format(reportedPositionX))
        self.reportedPositionY.setText("{:.5f}".format(reportedPositionY))
        self.reportedPositionZ.setText("{:.5f}".format(reportedPositionZ))
        self.reportedPositionU.setText("{:.5f}".format(reportedPositionU))
        self.reportedPositionV.setText("{:.5f}".format(reportedPositionV))
        self.reportedPositionW.setText("{:.5f}".format(reportedPositionW))

        self.positionFollowingErrorX.setText("{:.5f}".format(positionFollowingErrorX))
        self.positionFollowingErrorY.setText("{:.5f}".format(positionFollowingErrorY))
        self.positionFollowingErrorZ.setText("{:.5f}".format(positionFollowingErrorZ))
        self.positionFollowingErrorU.setText("{:.5f}".format(positionFollowingErrorU))
        self.positionFollowingErrorV.setText("{:.5f}".format(positionFollowingErrorV))
        self.positionFollowingErrorW.setText("{:.5f}".format(positionFollowingErrorW))
