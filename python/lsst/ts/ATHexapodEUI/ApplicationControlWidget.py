
import QTHelpers
from lsst.ts.ATHexapodEUI.ATHexapodEnumerations import SummaryStates
from PySide2.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout)

class ApplicationControlWidget(QWidget):
    def __init__(self, ATHexapod):
        QWidget.__init__(self)
        self.ATHexapod = ATHexapod
        self.layout = QVBoxLayout()
        self.commandLayout = QVBoxLayout()
        self.layout.addLayout(self.commandLayout)
        self.setLayout(self.layout)

        self.button1 = QPushButton("Button1")
        QTHelpers.updateSizePolicy(self.button1)
        self.button1.clicked.connect(QTHelpers.doNothing)
        QTHelpers.hideButton(self.button1)
        self.button2 = QPushButton("Button2")
        QTHelpers.updateSizePolicy(self.button2)
        self.button2.clicked.connect(QTHelpers.doNothing)
        QTHelpers.hideButton(self.button2)
        self.button3 = QPushButton("Button3")
        QTHelpers.updateSizePolicy(self.button3)
        self.button3.clicked.connect(QTHelpers.doNothing)
        QTHelpers.hideButton(self.button3)
        self.button4 = QPushButton("Button4")
        QTHelpers.updateSizePolicy(self.button4)
        self.button4.clicked.connect(QTHelpers.doNothing)
        QTHelpers.hideButton(self.button4)

        self.commandLayout.addWidget(self.button1)
        self.commandLayout.addWidget(self.button2)
        self.commandLayout.addWidget(self.button3)
        self.commandLayout.addWidget(self.button4)
        
        self.ATHexapod.subscribeEvent_summaryState(self.processEventSummaryState)

    def issueCommandStart(self):
        self.ATHexapod.issueCommandThenWait_start("")

    def issueCommandEnable(self):
        self.ATHexapod.issueCommandThenWait_enable(False)

    def issueCommandDisable(self):
        self.ATHexapod.issueCommandThenWait_disable(False)

    def issueCommandStandby(self):
        self.ATHexapod.issueCommandThenWait_standby(False)

    def processEventSummaryState(self, data):
        state = data[-1].summaryState
        if state == SummaryStates.StandbyState:
            QTHelpers.updateButton(self.button1, "Start", self.issueCommandStart)
            QTHelpers.hideButton(self.button2)
            QTHelpers.hideButton(self.button3)
            QTHelpers.hideButton(self.button4)
        elif state == SummaryStates.DisabledState:
            QTHelpers.updateButton(self.button1, "Enable", self.issueCommandEnable)
            QTHelpers.hideButton(self.button2)
            QTHelpers.hideButton(self.button3)
            QTHelpers.updateButton(self.button4, "Standby", self.issueCommandStandby)
        elif state == SummaryStates.EnabledState:
            QTHelpers.hideButton(self.button1)
            QTHelpers.hideButton(self.button2)
            QTHelpers.hideButton(self.button3)
            QTHelpers.updateButton(self.button4, "Disable", self.issueCommandDisable)
        elif state == SummaryStates.FaultState:
            QTHelpers.hideButton(self.button1)
            QTHelpers.hideButton(self.button2)
            QTHelpers.hideButton(self.button3)
            QTHelpers.updateButton(self.button4, "Standby", self.issueCommandStandby)
        elif state == SummaryStates.OfflineState:
            QTHelpers.hideButton(self.button1)
            QTHelpers.hideButton(self.button2)
            QTHelpers.hideButton(self.button3)
            QTHelpers.hideButton(self.button4)
