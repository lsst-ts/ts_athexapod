import lsst.ts.pythonFileReader.ConfigurationFileReaderYaml as ryaml


class ConfigurationKeeper:

    def __init__(self):
        self.settingsPath = "./settingFile"
        self.mainConfiguration = ryaml.FileReaderYaml("./settingFiles", "", "")
        self.mainConfiguration.loadFile("mainSetup")
        self.local = ryaml.FileReaderYaml("./settingFiles", "", "")

    def updateConfiguration(settingsToApply):
        self.local.setSettingsFromLabel(settingsToApply, self.mainConfiguration)
        

class InitialHexapodSetup:
    self.limitXYMax = 22.5
    self.limitZMin = -12.5
    self.limitZMax = 12.5
    self.limitUVMax = 7.5
    self.limitWMin = -12.5
    self.limitWMax = 12.5
    self.velocityXYMax = 1
    self.velocityRxRyMax = 1
    self.velocityZMax = 1
    self.velocityRzMax = 1
    self.positionX = 0
    self.positionY = 0
    self.positionZ = 0
    self.positionU = 0
    self.positionV = 0
    self.positionW = 0
    self.pivotX = 0
    self.pivotY = 0
    self.pivotZ = 0


class TcpConfiguration:
    self.host = "139.229.136.151"
    self.port = 50000
    self.connectionTimeout = 2
    self.readTimeout = 2
    self.sendTimeout = 2
    self.endStr = "endl"
    self.maxLength = 1024
