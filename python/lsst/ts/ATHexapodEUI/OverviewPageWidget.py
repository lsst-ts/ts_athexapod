
import QTHelpers
from lsst.ts.ATHexapodEUI.ATHexapodEnumerations import SummaryStates
from lsst.ts.ATHexapodEUI.DataCache import DataCache
from pyqtgraph.Qt.QtGui import 


class OverviewPageWidget(QtGui.QWidget):
    def __init__(self, ATHexapod):
        QtGui.QWidget.__init__(self)
        self.ATHexapod = ATHexapod
        self.layout = QtGui.QVBoxLayout()
        self.dataLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.dataLayout)
        self.setLayout(self.layout)
        
        row = 0
        col = 0
        self.summaryStateLabel = QtGui.QLabel("UNKNOWN")
        self.dataLayout.addWidget(QtGui.QLabel("Summary State"), row, col)
        self.dataLayout.addWidget(self.summaryStateLabel, row, col + 1)

        self.dataEventSummaryState = DataCache()
        
        self.ATHexapod.subscribeEvent_summaryState(self.processEventSummaryState)
        
    def setPageActive(self, active):
        self.pageActive = active
        if self.pageActive:
            self.updatePage()

    def updatePage(self):
        if not self.pageActive:
            return 

        if self.dataEventSummaryState.hasBeenUpdated():
            data = self.dataEventSummaryState.get()
            state = data.summaryState
            summaryStateText = "UNKNOWN"
            if state == SummaryStates.OfflineState:
                summaryStateText = "Offline"
            elif state == SummaryStates.DisabledState:
                summaryStateText = "Disabled"
            elif state == SummaryStates.EnabledState:
                summaryStateText = "Enabled"
            elif state == SummaryStates.FaultState:
                summaryStateText = "Fault"
            self.summaryStateLabel.setText(summaryStates[state])

    def processEventSummaryState(self, data):
        self.dataEventSummaryState.set(data[-1])
