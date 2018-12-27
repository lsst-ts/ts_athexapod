import lsst.ts.pythonFileReader.ConfigurationFileReaderYaml as ryaml


class ConfigurationKeeper:

    def __init__(self):
        self.settingsPath = "./settingFile"
        self.mainConfiguration = ryaml.FileReaderYaml("./settingFiles", "", "")
        self.mainConfiguration.loadFile("mainSetup")
        self.localConfiguration = ryaml.FileReaderYaml("./settingFiles", "", "")

    def updateConfiguration(self, settingsToApply):
        """Update configuration according to a settingsToApply string
        Arguments:
            settingsToApply {String} -- Setting to apply label or version that comes from the start command
        """
        self.localConfiguration.setSettingsFromLabel(settingsToApply, self.mainConfiguration)

    def getInitialHexapodSetup(self):
        """Get ATHexapod initial state from file
        Returns:
            InitialHexapodSetup -- Initial setup of the ATHexapod
        """
        self.localConfiguration.loadFile("initialHexapodSetup")
        initialSetup = InitialHexapodSetup()
        initialSetup.limitXYMax = self.localConfiguration.readValue('limitXYMax')
        initialSetup.limitZMin = self.localConfiguration.readValue('limitZMin')
        initialSetup.limitZMax = self.localConfiguration.readValue('limitZMax')
        initialSetup.limitUVMax = self.localConfiguration.readValue('limitUVMax')
        initialSetup.limitWMin = self.localConfiguration.readValue('limitWMin')
        initialSetup.limitWMax = self.localConfiguration.readValue('limitWMax')
        initialSetup.velocityXYMax = self.localConfiguration.readValue('velocityXYMax')
        initialSetup.velocityRxRyMax = self.localConfiguration.readValue('velocityRxRyMax')
        initialSetup.velocityZMax = self.localConfiguration.readValue('velocityZMax')
        initialSetup.velocityRzMax = self.localConfiguration.readValue('velocityRzMax')
        initialSetup.positionX = self.localConfiguration.readValue('positionX')
        initialSetup.positionY = self.localConfiguration.readValue('positionY')
        initialSetup.positionZ = self.localConfiguration.readValue('positionZ')
        initialSetup.positionU = self.localConfiguration.readValue('positionU')
        initialSetup.positionV = self.localConfiguration.readValue('positionV')
        initialSetup.positionW = self.localConfiguration.readValue('positionW')
        initialSetup.pivotX = self.localConfiguration.readValue('pivotX')
        initialSetup.pivotY = self.localConfiguration.readValue('pivotY')
        initialSetup.pivotZ = self.localConfiguration.readValue('pivotZ')
        return initialSetup

    def getTcpConfiguration(self):
        """Get Tcp configuration from file
        Returns:
            tcpConfiguration -- Tcp configuration
        """
        self.localConfiguration.loadFile("tcpConfiguration")
        tcpConfiguration = TcpConfiguration()
        tcpConfiguration.host = self.localConfiguration.readValue('host')
        tcpConfiguration.port = self.localConfiguration.readValue('port')
        tcpConfiguration.connectionTimeout = self.localConfiguration.readValue('connectionTimeout')
        tcpConfiguration.readTimeout = self.localConfiguration.readValue('readTimeout')
        tcpConfiguration.sendTimeout = self.localConfiguration.readValue('sendTimeout')
        tcpConfiguration.endStr = self.localConfiguration.readValue('endStr')
        tcpConfiguration.maxLength = self.localConfiguration.readValue('maxLength')
        return tcpConfiguration

    def getSettingVersions(self):
        """Return string with comma separated values as recommended Settings

        Returns:
            [String] -- list of recommended settings
        """

        return self.mainConfiguration.getRecommendedSettings()


class InitialHexapodSetup:
    def __init__(self):
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
    def __init__(self):
        self.host = "139.229.136.151"
        self.port = 50000
        self.connectionTimeout = 2
        self.readTimeout = 2
        self.sendTimeout = 2
        self.endStr = "endl"
        self.maxLength = 1024
