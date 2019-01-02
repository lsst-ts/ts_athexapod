#!/usr/bin/python3
# -'''- coding: utf-8 -'''-

import sys
import time

from lsst.ts.ATHexapodEUI.ATHexapodRemote import ATHexapodRemote

from lsst.ts.ATHexapodEUI.ApplicationControlWidget import ApplicationControlWidget
from lsst.ts.ATHexapodEUI.ApplicationStatusWidget import ApplicationStatusWidget
from lsst.ts.ATHexapodEUI.ApplicationPaginationWidget import ApplicationPaginationWidget
from lsst.ts.ATHexapodEUI.HexapodControlsPageWidget import HexapodControlsPageWidget
from lsst.ts.ATHexapodEUI.OverviewPageWidget import OverviewPageWidget

from pyqtgraph.Qt import QtGui
from PyQt5.QtCore import QTimer


class EUI(QtGui.QDialog):
    def __init__(self, ATHexapod, parent=None):
        super(EUI, self).__init__(parent)
        self.ATHexapod = ATHexapod
        self.layout = QtGui.QVBoxLayout()
        self.topLayerLayout = QtGui.QHBoxLayout()
        self.applicationControl = ApplicationControlWidget(ATHexapod)
        self.topLayerLayout.addWidget(self.applicationControl)
        self.applicationStatus = ApplicationStatusWidget(ATHexapod)
        self.topLayerLayout.addWidget(self.applicationStatus)
        self.middleLayerLayout = QtGui.QHBoxLayout()
        self.applicationPagination = ApplicationPaginationWidget(ATHexapod)
        self.applicationPagination.addPage("Overview", OverviewPageWidget(ATHexapod))
        self.applicationPagination.addPage("Controls", HexapodControlsPageWidget(ATHexapod))
        self.middleLayerLayout.addWidget(self.applicationPagination)
        self.bottomLayerLayout = QtGui.QHBoxLayout()
        self.layout.addLayout(self.topLayerLayout)
        self.layout.addLayout(self.middleLayerLayout)
        self.layout.addLayout(self.bottomLayerLayout)
        self.setLayout(self.layout)

if __name__ == '__main__':
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    # Create EUI
    ATHexapod = ATHexapodRemote()
    eui = EUI(ATHexapod)
    eui.show()
    # Create ATHexapod Telemetry & Event Loop
    telemetryEventLoopTimer = QTimer()
    telemetryEventLoopTimer.timeout.connect(ATHexapod.runSubscriberChecks)
    telemetryEventLoopTimer.start(500)
    # Run the main Qt loop
    app.exec_()
    # Clean up ATHexapod Telemetry & Event Loop
    telemetryEventLoopTimer.stop()
    # Close application
    sys.exit()
