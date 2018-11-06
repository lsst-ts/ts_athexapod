from enum import Enum

class ElectrometerCommand:

    def __init__(self):
        self.device = TestDevice()

    #Activate/deactivate a type of filter
    def activateFilter(self, mode, filterType, active):
        command = ":SENS:"
        command += mode.name+":"+filterType.name+":STAT "
        command += "1" if active else "0"
        command += ";"
        return command

    #Get the type of average filter the device is using
    def getAvgFilterStatus(self, mode):
        command = ":SENS:"
        command += mode.name
        command += ":AVER:TYPE?;"
        return command

    #Get the type of median filter the device is using
    def getMedFilterStatus(self, mode):
        command = ":SENS:"
        command += mode.name
        command += ":MED:STAT?;"
        return command

    #Get filter status
    def getFilterStatus(self, mode, filterType):
        command = ":SENS:"
        command += mode.name+":"
        command += filterType.name
        command += ":STAT?;"
        return command

    #Set the type of average filter to set
    def setAvgFilterStatus(self, mode, averFilterType):
        command = ":SENS:"
        command += mode.name
        command += ":AVER:TYPE "
        command += averFilterType.name+";"
        return command

    #Set the type of median filter to set
    def setMedFilterStatus(self, mode, active):
        command = ":SENS:"
        command += mode.name
        command += ":MED:STAT "
        command += "1" if active else "0"
        command += ";"
        return command

    #Always read value a store them into the buffer
    def alwaysRead(self):
        command = ":TRAC:FEED:CONT ALW;"
        command += "\n:INIT;"
        return command

    #Read value a store them into the buffer until the buffer is full
    def nextRead(self):
        command = ":TRAC:FEED:CONT NEXT;"
        command += "\n:INIT;"
        return command

    #Clear device buffer
    def clearBuffer(self):
        command = ":TRAC:CLE;"
        return command

    #Clear device buffer
    def clearDevice(self):
        command = "^C"
        return command

    #Get error query
    def getLastError(self):
        command = ":SYST:ERR?;"
        return command


    #Format the reads to include values from input
    def formatTrac(self, channel, timestamp, temperature):
        isFirst = True
        if(not (timestamp or temperature or channel)):
            command = ":TRAC:ELEM NONE"
        else:
            command = ":TRAC:ELEM "
            if (channel):
                isFirst = False
                command += "CHAN"
            if(timestamp):
                if (not isFirst): command += ", "
                isFirst = False
                command += "TST"
            if (temperature):
                if (not isFirst): command += ", "
                isFirst = False
                command += "ETEM"
        command += ";"
        return command

    #Get the quantity of values stored in the buffer
    def getBufferQuantity(self):
        command = ":TRAC:POIN:ACT?;"
        return command

    #Get hardware info
    def getHardwareInfo(self):
        command = "*IDN?"
        return command

    def getMeasure(self, readOption):
        if(readOption == readingOption.LATEST):
            command = ":SENS:DATA?;"
        else:
            command = ":SENS:DATA:FRES?;"
        return command

    def getMode(self):
        command = ":SENS:FUNC?;"
        return command

    def enableTemperatureReading(self, enable):
        if(enable):
            command = ":SYST:TSC ON;"
        else:
            command = ":SYST:TSC OFF;"
        return command

    #Command to read the buffer, don't read all in one read. Split in a small ammount of byte (256)
    #The electrometer will hang if reading all at once
    def readBuffer(self):
        command = ":TRAC:DATA?;"
        return command

    def resetDevice(self):
        command = "*RST;\n:TRACE:CLEAR;"
        return command

    def selectDeviceTimer(self, timer=0.001):
        command = "TRIG:SOUR TIM;\nTRIG:TIM "+'{0:.3f}'.format(timer)+";"
        return command

    def setBufferSize(self, bufferSize=50000):
        command = ":TRACE:CLEAR;\n:TRAC:POINTS "+str(bufferSize)+";\n:TRIG:COUNT "+str(bufferSize)+";"
        return command

    def initBuffer(self):
        command = ":INIT;"
        return command

    def integrationTime(self, mode, time=0.001):
        command = ":SENS:"+mode.name+":APER "+str(time)+";"
        return command

    def setMode(self, mode):
        command = ":SENS:FUNC '"+mode.name+"';"
        return command

    def setRange(self, auto, rangeValue, mode):
        if(auto):
            command = ":SENS:"+mode.name+":RANG:AUTO 1;"
        else:
            command = ":SENS:"+mode.name+":RANG:AUTO 0;"
            command += "\n:SENS:"+mode.name+":RANG "+str(rangeValue)+";"
        return command

    def enableSync(self, enable):
        command = ":SYSTEM:LSYN:STAT ON;" if enable else ":SYSTEM:LSYN:STAT OFF;"
        return command

    def stopReadingBuffer(self):
        command = ":TRAC:FEED:CONT NEV;"
        return command

    def enableAllInstrumentErrors(self):
        command = ":STAT:QUE:ENAB (-440:+958);"
        return command

    def enableZeroCheck(self, enable):
        command = ":SYST:ZCH ON;" if enable else ":SYST:ZCH OFF;"
        return command

    def enableZeroCorrection(self, enable):
        command = ":SYST:ZCOR ON;" if enable else ":SYST:ZCOR OFF;"
        return command

    def getRange(self, mode):
        command = ":SENS:"+mode.name+":RANG?;"
        return command

    def getIntegrationTime(self, mode):
        command = ":SENS:"+mode.name+":APER?;"
        return command

class UnitMode(Enum):
    CURR = 1
    CHAR = 2
    VOLT = 3
    RES = 4

class Filter(Enum):
    MED = 1
    AVER = 2

class AverFilterType(Enum):
    NONE = 1
    SCAL = 2
    ADV = 3

class readingOption(Enum):
    LATEST = 1  #Last value read
    NEWREAD = 2 #New reading

class TestDevice:
    def __init__(self):
        self.messageReceived = "getMessage executed..."
        self.messageToSend = "sendMessage executed: "
        self.connected = False

    def connect(self):
        self.connected = True

    def connect(self):
        self.connected = False

    def isConnected(self):
        return self.connected

    def getMessage(self):
        print(self.messageReceived)
        return self.messageReceived

    def sendMessage(self, message):
        print(self.messageToSend+message)
        return message

test = ElectrometerCommand()
test.activateFilter(mode=UnitMode.CURR, filterType=Filter.AVER, active=True)
