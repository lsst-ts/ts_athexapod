from lsst.ts.ATHexapodEUI.ATHexapodEnumerations import SummaryStates, DetailedState
from pyqtgraph.Qt import QtGui


class ApplicationStatusWidget(QtGui.QWidget):
    def __init__(self, ATHexapod):
        QtGui.QWidget.__init__(self)
        self.ATHexapod = ATHexapod
        self.layout = QtGui.QVBoxLayout()
        self.statusLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.statusLayout)
        self.setLayout(self.layout)

        self.summaryStateLabel = QtGui.QLabel("Offline")
        self.detailedStateLabel = QtGui.QLabel("UNKNOWN")

        row = 0
        col = 0
        self.statusLayout.addWidget(QtGui.QLabel("Summary State"), row, col)
        self.statusLayout.addWidget(self.summaryStateLabel, row, col + 1)
        self.statusLayout.addWidget(QtGui.QLabel("Detailed State"), row + 1, col)
        self.statusLayout.addWidget(self.detailedStateLabel, row + 1, col + 1)

        self.ATHexapod.subscribeEvent_summaryState(self.processEventSummaryState)
        self.ATHexapod.subscribeEvent_detailedState(self.processEventDetailedState)

    def processEventSummaryState(self, data):
        summaryState = data[-1].summaryState
        summaryStateText = "Unknown"
        if summaryState == SummaryStates.DisabledState:
            summaryStateText = "Disabled"
        elif summaryState == SummaryStates.EnabledState:
            summaryStateText = "Enabled"
        elif summaryState == SummaryStates.FaultState:
            summaryStateText = "Fault"
        elif summaryState == SummaryStates.OfflineState:
            summaryStateText = "Offline"
        elif summaryState == SummaryStates.StandbyState:
            summaryStateText = "Standby"

        self.summaryStateLabel.setText(summaryStateText)

    def processEventDetailedState(self, data):
        detailedState = data[-1].detailedState
        detailedStateText = "Unknown"
        if detailedState == DetailedState.InMotionState:
            detailedStateText = "InMotion"
        elif detailedState == DetailedState.NotInMotionState:
            detailedStateText = "NotInMotion"

        self.detailedStateLabel.setText(detailedStateText)
