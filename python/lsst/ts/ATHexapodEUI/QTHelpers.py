import numpy as np


def updateButton(button, text, action):
    button.setVisible(True)
    button.setText(text)
    button.clicked.disconnect()
    button.clicked.connect(action)


def doNothing():
    pass


def hideButton(button):
    button.setVisible(False)
    button.clicked.disconnect()
    button.clicked.connect(doNothing)


def onlyHideButton(button):
    button.setVisible(False)


def onlyShowButton(button):
    button.setVisible(True)


def updateSizePolicy(widget):
    policy = widget.sizePolicy()
    policy.setRetainSizeWhenHidden(True)
    widget.setSizePolicy(policy)


def setBoolLabel(label, trueText, falseText, value):
    text = falseText
    if value:
        text = trueText
    label.setText(text)


def setWarningLabel(label, value):
    setBoolLabel(label, "WARNING", "OK", value)


def setBoolLabelHighLow(label, value):
    setBoolLabel(label, "HIGH", "LOW", value)


def setBoolLabelOnOff(label, value):
    setBoolLabel(label, "ON", "OFF", value)


def setBoolLabelOpenClosed(label, value):
    setBoolLabel(label, "OPEN", "CLOSED", value)


def appendAndResizeCurveData(data, newData, limit):
    data = np.insert(data, 0, newData)
    if len(data) > limit:
        data = np.delete(data, np.arange(limit, len(data)))
    return data
