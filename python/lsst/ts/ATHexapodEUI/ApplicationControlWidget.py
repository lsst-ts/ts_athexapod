
from lsst.ts.ATHexapodEUI import QTHelpers
from lsst.ts.ATHexapodEUI.ATHexapodEnumerations import SummaryStates
from pyqtgraph.Qt import QtGui


class ApplicationControlWidget(QtGui.QWidget):
    def __init__(self, ATHexapod):
        QtGui.QWidget.__init__(self)
        self.ATHexapod = ATHexapod
        self.layout = QtGui.QVBoxLayout()
        self.commandLayout = QtGui.QVBoxLayout()
        self.layout.addLayout(self.commandLayout)
        self.setLayout(self.layout)

        self.button1 = QtGui.QPushButton("Button1")
        QTHelpers.updateSizePolicy(self.button1)
        self.button1.clicked.connect(QTHelpers.doNothing)
        QTHelpers.hideButton(self.button1)
        self.button2 = QtGui.QPushButton("Button2")
        QTHelpers.updateSizePolicy(self.button2)
        self.button2.clicked.connect(QTHelpers.doNothing)
        QTHelpers.hideButton(self.button2)
        self.button3 = QtGui.QPushButton("Button3")
        QTHelpers.updateSizePolicy(self.button3)
        self.button3.clicked.connect(QTHelpers.doNothing)
        QTHelpers.hideButton(self.button3)
        self.button4 = QtGui.QPushButton("Button4")
        QTHelpers.updateSizePolicy(self.button4)
        self.button4.clicked.connect(QTHelpers.doNothing)
        QTHelpers.hideButton(self.button4)

        self.settingVersions = QtGui.QComboBox()

        self.commandLayout.addWidget(self.button1)
        self.commandLayout.addWidget(self.button2)
        self.commandLayout.addWidget(self.button3)
        self.commandLayout.addWidget(self.button4)
        self.commandLayout.addWidget(self.settingVersions)

        self.ATHexapod.subscribeEvent_summaryState(self.processEventSummaryState)
        self.ATHexapod.subscribeEvent_settingVersions(self.processEventSettingVersions)

    def issueCommandStart(self):
        self.ATHexapod.issueCommand_start(self.settingVersions.currentText())

    def issueCommandEnable(self):
        self.ATHexapod.issueCommand_enable(False)

    def issueCommandDisable(self):
        self.ATHexapod.issueCommand_disable(False)

    def issueCommandStandby(self):
        self.ATHexapod.issueCommand_standby(False)

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

    def processEventSettingVersions(self, data):
        settingVersions = data[-1].recommendedSettingsVersion
        settingLabels = data[-1].recommendedSettingsLabels
        self.settingVersions.clear()
        if(settingVersions):
            for i in settingVersions.split(","):
                self.settingVersions.addItem(i)
        if(settingLabels):
            for i in settingLabels.split(","):
                self.settingVersions.addItem(i)
