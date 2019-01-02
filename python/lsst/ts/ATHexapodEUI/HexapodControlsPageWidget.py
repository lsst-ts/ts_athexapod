from lsst.ts.ATHexapodEUI import QTHelpers
from lsst.ts.ATHexapodEUI.ATHexapodEnumerations import SummaryStates
from lsst.ts.ATHexapodEUI.DataCache import DataCache
from pyqtgraph.Qt import QtGui


class HexapodControlsPageWidget(QtGui.QWidget):
    def __init__(self, ATHexapod):
        QtGui.QWidget.__init__(self)
        self.ATHexapod = ATHexapod
        self.layout = QtGui.QGridLayout()
        self.controlsLayout = QtGui.QGridLayout()
        self.dataLayout = QtGui.QGridLayout()

        self.layout.addLayout(self.controlsLayout, 0, 0)
        self.layout.addLayout(self.dataLayout, 1, 0)
        self.setLayout(self.layout)

        # Define buttons
        self.applyPositionLimitsButton = QtGui.QPushButton("applyPositionLimits")
        QTHelpers.updateSizePolicy(self.applyPositionLimitsButton)
        self.applyPositionLimitsButton.clicked.connect(self.issueCommandapplyPositionLimits)

        self.moveToPositionButon = QtGui.QPushButton("moveToPosition")
        QTHelpers.updateSizePolicy(self.moveToPositionButon)
        self.moveToPositionButon.clicked.connect(self.issueCommandMoveToPosition)

        self.setMaxSpeedsButton = QtGui.QPushButton("setMaxSpeeds")
        QTHelpers.updateSizePolicy(self.setMaxSpeedsButton)
        self.setMaxSpeedsButton.clicked.connect(self.issueCommandApplyVelocityLimits)

        self.applyPositionOffsetButton = QtGui.QPushButton("applyPositionOffset")
        QTHelpers.updateSizePolicy(self.applyPositionOffsetButton)
        self.applyPositionOffsetButton.clicked.connect(self.issueCommandApplyPositionOffset)

        self.stopAllAxesButton = QtGui.QPushButton("stopAllAxes")
        QTHelpers.updateSizePolicy(self.stopAllAxesButton)
        self.stopAllAxesButton.clicked.connect(self.issueCommandStopMotionAllAxes)

        self.pivotButton = QtGui.QPushButton("pivot")
        QTHelpers.updateSizePolicy(self.pivotButton)
        self.pivotButton.clicked.connect(self.issueCommandPivot)

        row = 0
        col = 0
        self.label = QtGui.QLabel("ATHexapod Controls")
        self.controlsLayout.addWidget(self.label)
        row += 1
        # Add applyPositionLimit control
        self.addApplyPositionLimitsControl(row, col)
        row += 2
        self.addMoveToPositionControl(row, col)
        row += 2
        self.addApplyVelocityLimitsButtonControl(row, col)
        row += 2
        self.addStopAllAxesButtonControl(row, col)
        row += 2
        self.addPivotButtonControl(row, col)
        row += 2
        self.addApplyPositionOffsetButtonControl(row, col)
        row += 2
        col = 0

        self.ATHexapod.subscribeEvent_summaryState(self.processEventSummaryState)

    def setPageActive(self, active):
        self.pageActive = active
        if self.pageActive:
            self.updatePage()

    def updatePage(self):
        if not self.pageActive:
            return

    def processEventSummaryState(self, data):
        state = data[-1].summaryState
        if state != SummaryStates.EnabledState:
            QTHelpers.onlyHideButton(self.applyPositionLimitsButton)
            QTHelpers.onlyHideButton(self.moveToPositionButon)
            QTHelpers.onlyHideButton(self.setMaxSpeedsButton)
            QTHelpers.onlyHideButton(self.applyPositionOffsetButton)
            QTHelpers.onlyHideButton(self.stopAllAxesButton)
            QTHelpers.onlyHideButton(self.pivotButton)
        else:
            QTHelpers.onlyShowButton(self.applyPositionLimitsButton)
            QTHelpers.onlyShowButton(self.moveToPositionButon)
            QTHelpers.onlyShowButton(self.setMaxSpeedsButton)
            QTHelpers.onlyShowButton(self.applyPositionOffsetButton)
            QTHelpers.onlyShowButton(self.stopAllAxesButton)
            QTHelpers.onlyShowButton(self.pivotButton)

    def issueCommandapplyPositionLimits(self):
        xyMax = float(self.xyMax.text())
        zMin = float(self.zMin.text())
        zMax = float(self.zMax.text())
        uvMax = float(self.uvMax.text())
        wMin = float(self.wMin.text())
        wMax = float(self.wMax.text())
        self.ATHexapod.issueCommand_applyPositionLimits(xyMax, zMin, zMax, uvMax, wMin, wMax)

    def addApplyPositionLimitsControl(self, row, col):
        """Add button and inputs for applyPositionLimitsControl to qwidget

        Arguments:
            row {int} -- Starting row
            col {int} -- Starting column
        """

        row += 1
        self.xyMax = QtGui.QLineEdit()
        self.xyMax.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.xyMax.setText("22.5")
        self.zMin = QtGui.QLineEdit()
        self.zMin.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.zMin.setText("-12.5")
        self.zMax = QtGui.QLineEdit()
        self.zMax.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.zMax.setText("12.5")
        self.uvMax = QtGui.QLineEdit()
        self.uvMax.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.uvMax.setText("7.5")
        self.wMin = QtGui.QLineEdit()
        self.wMin.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.wMin.setText("-12.5")
        self.wMax = QtGui.QLineEdit()
        self.wMax.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.wMax.setText("12.5")

        self.controlsLayout.addWidget(self.applyPositionLimitsButton, row + 1, col)

        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("xyMax"), row, col)
        self.controlsLayout.addWidget(self.xyMax, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("zMin"), row, col)
        self.controlsLayout.addWidget(self.zMin, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("zMax"), row, col)
        self.controlsLayout.addWidget(self.zMax, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("uvMax"), row, col)
        self.controlsLayout.addWidget(self.uvMax, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("wMin"), row, col)
        self.controlsLayout.addWidget(self.wMin, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("wMax"), row, col)
        self.controlsLayout.addWidget(self.wMax, row + 1, col)
        col += 1

    def issueCommandMoveToPosition(self):
        x = float(self.x.text())
        y = float(self.y.text())
        z = float(self.z.text())
        u = float(self.u.text())
        v = float(self.v.text())
        w = float(self.w.text())
        self.ATHexapod.issueCommand_moveToPosition(x, y, z, u, v, w)

    def addMoveToPositionControl(self, row, col):
        """Add button and inputs for moveToPosition to qwidget

        Arguments:
            row {int} -- Starting row
            col {int} -- Starting column
        """

        row += 1
        self.x = QtGui.QLineEdit()
        self.x.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.x.setText("0")
        self.y = QtGui.QLineEdit()
        self.y.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.y.setText("0")
        self.z = QtGui.QLineEdit()
        self.z.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.z.setText("0")
        self.u = QtGui.QLineEdit()
        self.u.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.u.setText("0")
        self.v = QtGui.QLineEdit()
        self.v.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.v.setText("0")
        self.w = QtGui.QLineEdit()
        self.w.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.w.setText("0")

        self.controlsLayout.addWidget(self.moveToPositionButon, row + 1, col)

        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("x"), row, col)
        self.controlsLayout.addWidget(self.x, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("y"), row, col)
        self.controlsLayout.addWidget(self.y, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("x"), row, col)
        self.controlsLayout.addWidget(self.z, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("y"), row, col)
        self.controlsLayout.addWidget(self.u, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("v"), row, col)
        self.controlsLayout.addWidget(self.v, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("w"), row, col)
        self.controlsLayout.addWidget(self.w, row + 1, col)

    def issueCommandApplyPositionOffset(self):
        xOffset = float(self.xOffset.text())
        yOffset = float(self.yOffset.text())
        zOffset = float(self.zOffset.text())
        uOffset = float(self.uOffset.text())
        vOffset = float(self.vOffset.text())
        wOffset = float(self.wOffset.text())
        self.ATHexapod.issueCommand_applyPositionOffset(xOffset, yOffset, zOffset,
                                                        uOffset, vOffset, wOffset)

    def addApplyPositionOffsetButtonControl(self, row, col):
        """Add button and inputs for Apply Position Offset to qwidget

        Arguments:
            row {int} -- Starting row
            col {int} -- Starting column
        """

        row += 1
        self.xOffset = QtGui.QLineEdit()
        self.xOffset.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.xOffset.setText("0")
        self.yOffset = QtGui.QLineEdit()
        self.yOffset.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.yOffset.setText("0")
        self.zOffset = QtGui.QLineEdit()
        self.zOffset.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.zOffset.setText("0")
        self.uOffset = QtGui.QLineEdit()
        self.uOffset.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.uOffset.setText("0")
        self.vOffset = QtGui.QLineEdit()
        self.vOffset.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.vOffset.setText("0")
        self.wOffset = QtGui.QLineEdit()
        self.wOffset.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.wOffset.setText("0")

        self.controlsLayout.addWidget(self.applyPositionOffsetButton, row + 1, col)

        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("xOffset"), row, col)
        self.controlsLayout.addWidget(self.xOffset, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("yOffset"), row, col)
        self.controlsLayout.addWidget(self.yOffset, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("xOffset"), row, col)
        self.controlsLayout.addWidget(self.zOffset, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("yOffset"), row, col)
        self.controlsLayout.addWidget(self.uOffset, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("vOffset"), row, col)
        self.controlsLayout.addWidget(self.vOffset, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("wOffset"), row, col)
        self.controlsLayout.addWidget(self.wOffset, row + 1, col)

    def issueCommandPivot(self):
        xPivot = float(self.xPivot.text())
        yPivot = float(self.yPivot.text())
        zPivot = float(self.zPivot.text())
        self.ATHexapod.issueCommand_pivot(xPivot, yPivot, zPivot)

    def addPivotButtonControl(self, row, col):
        """Add button and inputs for Pivot to qwidget

        Arguments:
            row {int} -- Starting row
            col {int} -- Starting column
        """

        row += 1
        self.xPivot = QtGui.QLineEdit()
        self.xPivot.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.xPivot.setText("0")
        self.yPivot = QtGui.QLineEdit()
        self.yPivot.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.yPivot.setText("0")
        self.zPivot = QtGui.QLineEdit()
        self.zPivot.setValidator(QtGui.QDoubleValidator(-30, 30, 3))
        self.zPivot.setText("0")

        self.controlsLayout.addWidget(self.pivotButton, row + 1, col)

        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("xPivot"), row, col)
        self.controlsLayout.addWidget(self.xPivot, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("yPivot"), row, col)
        self.controlsLayout.addWidget(self.yPivot, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("xPivot"), row, col)
        self.controlsLayout.addWidget(self.zPivot, row + 1, col)

    def issueCommandStopMotionAllAxes(self):
        self.ATHexapod.issueCommand_stopAllAxes(True)

    def addStopAllAxesButtonControl(self, row, col):
        """Add stop button to qwidget

        Arguments:
            row {int} -- Starting row
            col {int} -- Starting column
        """
        row += 1

        self.stopAll = QtGui.QLineEdit()
        self.stopAll.setText("True")
        self.stopAll.setReadOnly(True)

        self.controlsLayout.addWidget(self.stopAllAxesButton, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("Stop"), row, col)
        self.controlsLayout.addWidget(self.stopAll, row + 1, col)

    def issueCommandApplyVelocityLimits(self):
        xyVelMax = float(self.xyVelMax.text())
        rxryVelMax = float(self.rxryVelMax.text())
        zVelMax = float(self.zVelMax.text())
        rzVelMax = float(self.rzVelMax.text())

        self.ATHexapod.issueCommand_setMaxSpeeds(xyVelMax, rxryVelMax, zVelMax, rzVelMax)

    def addApplyVelocityLimitsButtonControl(self, row, col):
        """Add button and inputs for Apply Position Offset to qwidget

        Arguments:
            row {int} -- Starting row
            col {int} -- Starting column
        """

        row += 1
        self.xyVelMax = QtGui.QLineEdit()
        self.xyVelMax.setValidator(QtGui.QDoubleValidator(-5, 5, 3))
        self.xyVelMax.setText("0")
        self.rxryVelMax = QtGui.QLineEdit()
        self.rxryVelMax.setValidator(QtGui.QDoubleValidator(-5, 5, 3))
        self.rxryVelMax.setText("0")
        self.zVelMax = QtGui.QLineEdit()
        self.zVelMax.setValidator(QtGui.QDoubleValidator(-5, 5, 3))
        self.zVelMax.setText("0")
        self.rzVelMax = QtGui.QLineEdit()
        self.rzVelMax.setValidator(QtGui.QDoubleValidator(-5, 5, 3))
        self.rzVelMax.setText("0")

        self.controlsLayout.addWidget(self.setMaxSpeedsButton, row + 1, col)

        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("xyVelMax"), row, col)
        self.controlsLayout.addWidget(self.xyVelMax, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("rxryVelMax"), row, col)
        self.controlsLayout.addWidget(self.rxryVelMax, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("zVelMax"), row, col)
        self.controlsLayout.addWidget(self.zVelMax, row + 1, col)
        col += 1
        self.controlsLayout.addWidget(QtGui.QLabel("rzVelMax"), row, col)
        self.controlsLayout.addWidget(self.rzVelMax, row + 1, col)
