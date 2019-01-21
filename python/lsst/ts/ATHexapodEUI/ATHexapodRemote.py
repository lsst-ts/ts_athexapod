import time
from SALPY_ATHexapod import *


class ATHexapodRemote:
    def __init__(self, index=0):
        self.sal = SAL_ATHexapod(index)
        self.sal.setDebugLevel(0)
        self.sal.salCommand("ATHexapod_command_abort")
        self.sal.salCommand("ATHexapod_command_enable")
        self.sal.salCommand("ATHexapod_command_disable")
        self.sal.salCommand("ATHexapod_command_standby")
        self.sal.salCommand("ATHexapod_command_exitControl")
        self.sal.salCommand("ATHexapod_command_start")
        self.sal.salCommand("ATHexapod_command_enterControl")
        self.sal.salCommand("ATHexapod_command_setLogLevel")
        self.sal.salCommand("ATHexapod_command_setSimulationMode")
        self.sal.salCommand("ATHexapod_command_setValue")
        self.sal.salCommand("ATHexapod_command_applyPositionLimits")
        self.sal.salCommand("ATHexapod_command_moveToPosition")
        self.sal.salCommand("ATHexapod_command_setMaxSystemSpeeds")
        self.sal.salCommand("ATHexapod_command_applyPositionOffset")
        self.sal.salCommand("ATHexapod_command_stopAllAxes")
        self.sal.salCommand("ATHexapod_command_pivot")

        self.sal.salEvent("ATHexapod_logevent_settingVersions")
        self.sal.salEvent("ATHexapod_logevent_errorCode")
        self.sal.salEvent("ATHexapod_logevent_summaryState")
        self.sal.salEvent("ATHexapod_logevent_appliedSettingsMatchStart")
        self.sal.salEvent("ATHexapod_logevent_logLevel")
        self.sal.salEvent("ATHexapod_logevent_logMessage")
        self.sal.salEvent("ATHexapod_logevent_simulationMode")
        self.sal.salEvent("ATHexapod_logevent_inPosition")
        self.sal.salEvent("ATHexapod_logevent_heartbeat")
        self.sal.salEvent("ATHexapod_logevent_detailedState")
        self.sal.salEvent("ATHexapod_logevent_settingsAppliedPositionLimits")
        self.sal.salEvent("ATHexapod_logevent_settingsAppliedVelocities")
        self.sal.salEvent("ATHexapod_logevent_settingsAppliedPivot")
        self.sal.salEvent("ATHexapod_logevent_positionUpdate")
        self.sal.salEvent("ATHexapod_logevent_settingsAppliedTcp")
        self.sal.salEvent("ATHexapod_logevent_readyForCommand")

        self.sal.salTelemetrySub("ATHexapod_positionStatus")

        self.eventSubscribers_settingVersions = []
        self.eventSubscribers_errorCode = []
        self.eventSubscribers_summaryState = []
        self.eventSubscribers_appliedSettingsMatchStart = []
        self.eventSubscribers_logLevel = []
        self.eventSubscribers_logMessage = []
        self.eventSubscribers_simulationMode = []
        self.eventSubscribers_inPosition = []
        self.eventSubscribers_heartbeat = []
        self.eventSubscribers_detailedState = []
        self.eventSubscribers_settingsAppliedPositionLimits = []
        self.eventSubscribers_settingsAppliedVelocities = []
        self.eventSubscribers_settingsAppliedPivot = []
        self.eventSubscribers_positionUpdate = []
        self.eventSubscribers_settingsAppliedTcp = []
        self.eventSubscribers_readyForCommand = []

        self.telemetrySubscribers_positionStatus = []

        self.topicsSubscribedToo = {}

    def close(self):
        time.sleep(1)
        self.sal.salShutdown()

    def flush(self, action):
        result, data = action()
        while result >= 0:
            result, data = action()

    def checkForSubscriber(self, action, subscribers):
        buffer = []
        result, data = action()
        while result == 0:
            buffer.append(data)
            result, data = action()
        if len(buffer) > 0:
            for subscriber in subscribers:
                subscriber(buffer)

    def runSubscriberChecks(self):
        for subscribedTopic in self.topicsSubscribedToo:
            action = self.topicsSubscribedToo[subscribedTopic][0]
            subscribers = self.topicsSubscribedToo[subscribedTopic][1]
            self.checkForSubscriber(action, subscribers)

    def getEvent(self, action):
        lastResult, lastData = action()
        while lastResult >= 0:
            result, data = action()
            if result >= 0:
                lastResult = result
                lastData = data
            elif result < 0:
                break
        return lastResult, lastData

    def getTimestamp(self):
        return self.sal.getCurrentTime()

    def issueCommand_abort(self, value):
        data = ATHexapod_command_abortC()
        data.value = value

        return self.sal.issueCommand_abort(data)

    def getResponse_abort(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_abort(data)
        return result, data

    def waitForCompletion_abort(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_abort(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_abort()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_abort(self, value, timeoutInSeconds=10):
        cmdId = self.issueCommand_abort(value)
        return self.waitForCompletion_abort(cmdId, timeoutInSeconds)

    def issueCommand_enable(self, value):
        data = ATHexapod_command_enableC()
        data.value = value

        return self.sal.issueCommand_enable(data)

    def getResponse_enable(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_enable(data)
        return result, data

    def waitForCompletion_enable(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_enable(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_enable()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_enable(self, value, timeoutInSeconds=10):
        cmdId = self.issueCommand_enable(value)
        return self.waitForCompletion_enable(cmdId, timeoutInSeconds)

    def issueCommand_disable(self, value):
        data = ATHexapod_command_disableC()
        data.value = value

        return self.sal.issueCommand_disable(data)

    def getResponse_disable(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_disable(data)
        return result, data

    def waitForCompletion_disable(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_disable(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_disable()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_disable(self, value, timeoutInSeconds=10):
        cmdId = self.issueCommand_disable(value)
        return self.waitForCompletion_disable(cmdId, timeoutInSeconds)

    def issueCommand_standby(self, value):
        data = ATHexapod_command_standbyC()
        data.value = value

        return self.sal.issueCommand_standby(data)

    def getResponse_standby(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_standby(data)
        return result, data

    def waitForCompletion_standby(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_standby(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_standby()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_standby(self, value, timeoutInSeconds=10):
        cmdId = self.issueCommand_standby(value)
        return self.waitForCompletion_standby(cmdId, timeoutInSeconds)

    def issueCommand_exitControl(self, value):
        data = ATHexapod_command_exitControlC()
        data.value = value

        return self.sal.issueCommand_exitControl(data)

    def getResponse_exitControl(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_exitControl(data)
        return result, data

    def waitForCompletion_exitControl(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_exitControl(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_exitControl()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_exitControl(self, value, timeoutInSeconds=10):
        cmdId = self.issueCommand_exitControl(value)
        return self.waitForCompletion_exitControl(cmdId, timeoutInSeconds)

    def issueCommand_start(self, settingsToApply):
        data = ATHexapod_command_startC()
        data.settingsToApply = settingsToApply

        return self.sal.issueCommand_start(data)

    def getResponse_start(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_start(data)
        return result, data

    def waitForCompletion_start(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_start(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_start()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_start(self, settingsToApply, timeoutInSeconds=10):
        cmdId = self.issueCommand_start(settingsToApply)
        return self.waitForCompletion_start(cmdId, timeoutInSeconds)

    def issueCommand_enterControl(self, value):
        data = ATHexapod_command_enterControlC()
        data.value = value

        return self.sal.issueCommand_enterControl(data)

    def getResponse_enterControl(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_enterControl(data)
        return result, data

    def waitForCompletion_enterControl(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_enterControl(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_enterControl()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_enterControl(self, value, timeoutInSeconds=10):
        cmdId = self.issueCommand_enterControl(value)
        return self.waitForCompletion_enterControl(cmdId, timeoutInSeconds)

    def issueCommand_setLogLevel(self, level):
        data = ATHexapod_command_setLogLevelC()
        data.level = level

        return self.sal.issueCommand_setLogLevel(data)

    def getResponse_setLogLevel(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_setLogLevel(data)
        return result, data

    def waitForCompletion_setLogLevel(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_setLogLevel(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_setLogLevel()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_setLogLevel(self, level, timeoutInSeconds=10):
        cmdId = self.issueCommand_setLogLevel(level)
        return self.waitForCompletion_setLogLevel(cmdId, timeoutInSeconds)

    def issueCommand_setSimulationMode(self, mode):
        data = ATHexapod_command_setSimulationModeC()
        data.mode = mode

        return self.sal.issueCommand_setSimulationMode(data)

    def getResponse_setSimulationMode(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_setSimulationMode(data)
        return result, data

    def waitForCompletion_setSimulationMode(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_setSimulationMode(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_setSimulationMode()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_setSimulationMode(self, mode, timeoutInSeconds=10):
        cmdId = self.issueCommand_setSimulationMode(mode)
        return self.waitForCompletion_setSimulationMode(cmdId, timeoutInSeconds)

    def issueCommand_setValue(self, parametersAndValues):
        data = ATHexapod_command_setValueC()
        data.parametersAndValues = parametersAndValues

        return self.sal.issueCommand_setValue(data)

    def getResponse_setValue(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_setValue(data)
        return result, data

    def waitForCompletion_setValue(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_setValue(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_setValue()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_setValue(self, parametersAndValues, timeoutInSeconds=10):
        cmdId = self.issueCommand_setValue(parametersAndValues)
        return self.waitForCompletion_setValue(cmdId, timeoutInSeconds)

    def issueCommand_applyPositionLimits(self, xyMax, zMin, zMax, uvMax, wMin, wMax):
        data = ATHexapod_command_applyPositionLimitsC()
        data.xyMax = xyMax
        data.zMin = zMin
        data.zMax = zMax
        data.uvMax = uvMax
        data.wMin = wMin
        data.wMax = wMax

        return self.sal.issueCommand_applyPositionLimits(data)

    def getResponse_applyPositionLimits(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_applyPositionLimits(data)
        return result, data

    def waitForCompletion_applyPositionLimits(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_applyPositionLimits(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_applyPositionLimits()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_applyPositionLimits(self, xyMax, zMin, zMax, uvMax, wMin, wMax,
                                                 timeoutInSeconds=10):
        cmdId = self.issueCommand_applyPositionLimits(xyMax, zMin, zMax, uvMax, wMin, wMax)
        return self.waitForCompletion_applyPositionLimits(cmdId, timeoutInSeconds)

    def issueCommand_moveToPosition(self, x, y, z, u, v, w):
        data = ATHexapod_command_moveToPositionC()
        data.x = x
        data.y = y
        data.z = z
        data.u = u
        data.v = v
        data.w = w

        return self.sal.issueCommand_moveToPosition(data)

    def getResponse_moveToPosition(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_moveToPosition(data)
        return result, data

    def waitForCompletion_moveToPosition(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_moveToPosition(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_moveToPosition()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_moveToPosition(self, x, y, z, u, v, w, timeoutInSeconds=10):
        cmdId = self.issueCommand_moveToPosition(x, y, z, u, v, w)
        return self.waitForCompletion_moveToPosition(cmdId, timeoutInSeconds)

    def issueCommand_setMaxSystemSpeeds(self, speed):
        data = ATHexapod_command_setMaxSystemSpeedsC()
        data.speed = speed

        return self.sal.issueCommand_setMaxSystemSpeeds(data)

    def getResponse_setMaxSystemSpeeds(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_setMaxSystemSpeeds(data)
        return result, data

    def waitForCompletion_setMaxSystemSpeeds(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_setMaxSystemSpeeds(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_setMaxSystemSpeeds()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_setMaxSystemSpeeds(self, speed, timeoutInSeconds=10):
        cmdId = self.issueCommand_setMaxSystemSpeeds(speed)
        return self.waitForCompletion_setMaxSystemSpeeds(cmdId, timeoutInSeconds)

    def issueCommand_applyPositionOffset(self, x, y, z, u, v, w):
        data = ATHexapod_command_applyPositionOffsetC()
        data.x = x
        data.y = y
        data.z = z
        data.u = u
        data.v = v
        data.w = w

        return self.sal.issueCommand_applyPositionOffset(data)

    def getResponse_applyPositionOffset(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_applyPositionOffset(data)
        return result, data

    def waitForCompletion_applyPositionOffset(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_applyPositionOffset(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_applyPositionOffset()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_applyPositionOffset(self, x, y, z, u, v, w, timeoutInSeconds=10):
        cmdId = self.issueCommand_applyPositionOffset(x, y, z, u, v, w)
        return self.waitForCompletion_applyPositionOffset(cmdId, timeoutInSeconds)

    def issueCommand_stopAllAxes(self, stopAllAxes):
        data = ATHexapod_command_stopAllAxesC()
        data.stopAllAxes = stopAllAxes

        return self.sal.issueCommand_stopAllAxes(data)

    def getResponse_stopAllAxes(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_stopAllAxes(data)
        return result, data

    def waitForCompletion_stopAllAxes(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_stopAllAxes(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_stopAllAxes()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_stopAllAxes(self, stopAllAxes, timeoutInSeconds=10):
        cmdId = self.issueCommand_stopAllAxes(stopAllAxes)
        return self.waitForCompletion_stopAllAxes(cmdId, timeoutInSeconds)

    def issueCommand_pivot(self, x, y, z):
        data = ATHexapod_command_pivotC()
        data.x = x
        data.y = y
        data.z = z

        return self.sal.issueCommand_pivot(data)

    def getResponse_pivot(self):
        data = ATHexapod_ackcmdC()
        result = self.sal.getResponse_pivot(data)
        return result, data

    def waitForCompletion_pivot(self, cmdId, timeoutInSeconds=10):
        waitResult = self.sal.waitForCompletion_pivot(cmdId, timeoutInSeconds)
        # ackResult, ack = self.getResponse_pivot()
        # return waitResult, ackResult, ack
        return waitResult

    def issueCommandThenWait_pivot(self, x, y, z, timeoutInSeconds=10):
        cmdId = self.issueCommand_pivot(x, y, z)
        return self.waitForCompletion_pivot(cmdId, timeoutInSeconds)

    def getNextEvent_settingVersions(self):
        data = ATHexapod_logevent_settingVersionsC()
        result = self.sal.getEvent_settingVersions(data)
        return result, data

    def getEvent_settingVersions(self):
        return self.getEvent(self.getNextEvent_settingVersions)

    def subscribeEvent_settingVersions(self, action):
        self.eventSubscribers_settingVersions.append(action)
        if "event_settingVersions" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_settingVersions"] = [
                self.getNextEvent_settingVersions, self.eventSubscribers_settingVersions]

    def getNextEvent_errorCode(self):
        data = ATHexapod_logevent_errorCodeC()
        result = self.sal.getEvent_errorCode(data)
        return result, data

    def getEvent_errorCode(self):
        return self.getEvent(self.getNextEvent_errorCode)

    def subscribeEvent_errorCode(self, action):
        self.eventSubscribers_errorCode.append(action)
        if "event_errorCode" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_errorCode"] = [
                self.getNextEvent_errorCode, self.eventSubscribers_errorCode]

    def getNextEvent_summaryState(self):
        data = ATHexapod_logevent_summaryStateC()
        result = self.sal.getEvent_summaryState(data)
        return result, data

    def getEvent_summaryState(self):
        return self.getEvent(self.getNextEvent_summaryState)

    def subscribeEvent_summaryState(self, action):
        self.eventSubscribers_summaryState.append(action)
        if "event_summaryState" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_summaryState"] = [
                self.getNextEvent_summaryState, self.eventSubscribers_summaryState]

    def getNextEvent_appliedSettingsMatchStart(self):
        data = ATHexapod_logevent_appliedSettingsMatchStartC()
        result = self.sal.getEvent_appliedSettingsMatchStart(data)
        return result, data

    def getEvent_appliedSettingsMatchStart(self):
        return self.getEvent(self.getNextEvent_appliedSettingsMatchStart)

    def subscribeEvent_appliedSettingsMatchStart(self, action):
        self.eventSubscribers_appliedSettingsMatchStart.append(action)
        if "event_appliedSettingsMatchStart" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_appliedSettingsMatchStart"] = [
                self.getNextEvent_appliedSettingsMatchStart, self.eventSubscribers_appliedSettingsMatchStart]

    def getNextEvent_logLevel(self):
        data = ATHexapod_logevent_logLevelC()
        result = self.sal.getEvent_logLevel(data)
        return result, data

    def getEvent_logLevel(self):
        return self.getEvent(self.getNextEvent_logLevel)

    def subscribeEvent_logLevel(self, action):
        self.eventSubscribers_logLevel.append(action)
        if "event_logLevel" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_logLevel"] = [
                self.getNextEvent_logLevel, self.eventSubscribers_logLevel]

    def getNextEvent_logMessage(self):
        data = ATHexapod_logevent_logMessageC()
        result = self.sal.getEvent_logMessage(data)
        return result, data

    def getEvent_logMessage(self):
        return self.getEvent(self.getNextEvent_logMessage)

    def subscribeEvent_logMessage(self, action):
        self.eventSubscribers_logMessage.append(action)
        if "event_logMessage" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_logMessage"] = [
                self.getNextEvent_logMessage, self.eventSubscribers_logMessage]

    def getNextEvent_simulationMode(self):
        data = ATHexapod_logevent_simulationModeC()
        result = self.sal.getEvent_simulationMode(data)
        return result, data

    def getEvent_simulationMode(self):
        return self.getEvent(self.getNextEvent_simulationMode)

    def subscribeEvent_simulationMode(self, action):
        self.eventSubscribers_simulationMode.append(action)
        if "event_simulationMode" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_simulationMode"] = [
                self.getNextEvent_simulationMode, self.eventSubscribers_simulationMode]

    def getNextEvent_inPosition(self):
        data = ATHexapod_logevent_inPositionC()
        result = self.sal.getEvent_inPosition(data)
        return result, data

    def getEvent_inPosition(self):
        return self.getEvent(self.getNextEvent_inPosition)

    def subscribeEvent_inPosition(self, action):
        self.eventSubscribers_inPosition.append(action)
        if "event_inPosition" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_inPosition"] = [
                self.getNextEvent_inPosition, self.eventSubscribers_inPosition]

    def getNextEvent_heartbeat(self):
        data = ATHexapod_logevent_heartbeatC()
        result = self.sal.getEvent_heartbeat(data)
        return result, data

    def getEvent_heartbeat(self):
        return self.getEvent(self.getNextEvent_heartbeat)

    def subscribeEvent_heartbeat(self, action):
        self.eventSubscribers_heartbeat.append(action)
        if "event_heartbeat" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_heartbeat"] = [
                self.getNextEvent_heartbeat, self.eventSubscribers_heartbeat]

    def getNextEvent_detailedState(self):
        data = ATHexapod_logevent_detailedStateC()
        result = self.sal.getEvent_detailedState(data)
        return result, data

    def getEvent_detailedState(self):
        return self.getEvent(self.getNextEvent_detailedState)

    def subscribeEvent_detailedState(self, action):
        self.eventSubscribers_detailedState.append(action)
        if "event_detailedState" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_detailedState"] = [
                self.getNextEvent_detailedState, self.eventSubscribers_detailedState]

    def getNextEvent_settingsAppliedPositionLimits(self):
        data = ATHexapod_logevent_settingsAppliedPositionLimitsC()
        result = self.sal.getEvent_settingsAppliedPositionLimits(data)
        return result, data

    def getEvent_settingsAppliedPositionLimits(self):
        return self.getEvent(self.getNextEvent_settingsAppliedPositionLimits)

    def subscribeEvent_settingsAppliedPositionLimits(self, action):
        self.eventSubscribers_settingsAppliedPositionLimits.append(action)
        if "event_settingsAppliedPositionLimits" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_settingsAppliedPositionLimits"] = [
                self.getNextEvent_settingsAppliedPositionLimits,
                self.eventSubscribers_settingsAppliedPositionLimits]

    def getNextEvent_settingsAppliedVelocities(self):
        data = ATHexapod_logevent_settingsAppliedVelocitiesC()
        result = self.sal.getEvent_settingsAppliedVelocities(data)
        return result, data

    def getEvent_settingsAppliedVelocities(self):
        return self.getEvent(self.getNextEvent_settingsAppliedVelocities)

    def subscribeEvent_settingsAppliedVelocities(self, action):
        self.eventSubscribers_settingsAppliedVelocities.append(action)
        if "event_settingsAppliedVelocities" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_settingsAppliedVelocities"] = [
                self.getNextEvent_settingsAppliedVelocities, self.eventSubscribers_settingsAppliedVelocities]

    def getNextEvent_settingsAppliedPivot(self):
        data = ATHexapod_logevent_settingsAppliedPivotC()
        result = self.sal.getEvent_settingsAppliedPivot(data)
        return result, data

    def getEvent_settingsAppliedPivot(self):
        return self.getEvent(self.getNextEvent_settingsAppliedPivot)

    def subscribeEvent_settingsAppliedPivot(self, action):
        self.eventSubscribers_settingsAppliedPivot.append(action)
        if "event_settingsAppliedPivot" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_settingsAppliedPivot"] = [
                self.getNextEvent_settingsAppliedPivot, self.eventSubscribers_settingsAppliedPivot]

    def getNextEvent_positionUpdate(self):
        data = ATHexapod_logevent_positionUpdateC()
        result = self.sal.getEvent_positionUpdate(data)
        return result, data

    def getEvent_positionUpdate(self):
        return self.getEvent(self.getNextEvent_positionUpdate)

    def subscribeEvent_positionUpdate(self, action):
        self.eventSubscribers_positionUpdate.append(action)
        if "event_positionUpdate" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_positionUpdate"] = [
                self.getNextEvent_positionUpdate, self.eventSubscribers_positionUpdate]

    def getNextEvent_settingsAppliedTcp(self):
        data = ATHexapod_logevent_settingsAppliedTcpC()
        result = self.sal.getEvent_settingsAppliedTcp(data)
        return result, data

    def getEvent_settingsAppliedTcp(self):
        return self.getEvent(self.getNextEvent_settingsAppliedTcp)

    def subscribeEvent_settingsAppliedTcp(self, action):
        self.eventSubscribers_settingsAppliedTcp.append(action)
        if "event_settingsAppliedTcp" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_settingsAppliedTcp"] = [
                self.getNextEvent_settingsAppliedTcp, self.eventSubscribers_settingsAppliedTcp]

    def getNextEvent_readyForCommand(self):
        data = ATHexapod_logevent_readyForCommandC()
        result = self.sal.getEvent_readyForCommand(data)
        return result, data

    def getEvent_readyForCommand(self):
        return self.getEvent(self.getNextEvent_readyForCommand)

    def subscribeEvent_readyForCommand(self, action):
        self.eventSubscribers_readyForCommand.append(action)
        if "event_readyForCommand" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["event_readyForCommand"] = [
                self.getNextEvent_readyForCommand, self.eventSubscribers_readyForCommand]

    def getNextSample_positionStatus(self):
        data = ATHexapod_positionStatusC()
        result = self.sal.getNextSample_positionStatus(data)
        return result, data

    def getSample_positionStatus(self):
        data = ATHexapod_positionStatusC()
        result = self.sal.getSample_positionStatus(data)
        return result, data

    def subscribeTelemetry_positionStatus(self, action):
        self.telemetrySubscribers_positionStatus.append(action)
        if "telemetry_positionStatus" not in self.topicsSubscribedToo:
            self.topicsSubscribedToo["telemetry_positionStatus"] = [
                self.getNextSample_positionStatus,
                self.telemetrySubscribers_positionStatus]
