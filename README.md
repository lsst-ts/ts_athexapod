# ts_salobjATHexapod

## How to install

### CSC
The application can be excecuted using a docker container as follow:
```sh
 $ docker pull lsstts/ts_athexapod
 $ docker run -it --net=host lsstts/ts_athexapod
 $ cd ~/repos/ts_salobjATHexapod/bin/
 $ runATHexapodCSC.py 0
```

### GUI
Give access to the docker to access to x11
```sh
 $ xhost +
```
Run container
```sh
 $ docker pull lsstts/ts_athexapod
 $ docker run -it -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --net=host --pid=host lsstts/ts_athexapod
```
Install dependencies
```sh
 $ cd ~/repos/ts_salobjATHexapod
 $ python ~/repos/ts_salobjATHexapod/python/lsst/ts/ATHexapodEUI/EUI.py
```
### EUI
Run the EUI executing using the instructions above. 
The GUI needs to be running before you execute the controller as the GUI gets information from summary state and updates the view according to it and cannot information prior to execution.  

Where 3 tabs are shown:
* Overview: 
  * Summary of the device. Currently only has all the events. The dropdown list has the list of recommended settings (needs to be Default1 to start)
![alt text][overview]

* Controls 
  * All the commands that can be executed (to see the commands, the application needs to be in EnabledState). The list of commands are:
    * applyPositionLimits: Set the limit for the positions (Also set in the configuration file)
    * moveToPosition: Move to a position for X, Y, Z, U, V and W.
    * setMaxSpeeds: Not implemented yet.
    * stopAllAxes: Stop all motion, it will only be accepted if the Hexapod is in motion. Its value in the GUI is a placeholder for organization purpose and is not settable 
    * pivot: Set the pivot in the PI Hexapod controller. Position needs to be 0 for U, V and W (Also set in the configuration file)
    * applyPositionOffset: Move an additional offset from current position.
![alt text][controls]

* Telemetry
  * Shows the current position of the ATHexapod. The CSC only update status when in Disabled or Enabled state.
![alt text][telemetry]

### Configuration
Configuration files
Inside the software folder there is a folder called settingFiles, inside this folder are:
* mainSetup.yaml : configuration file that is executed at run time. It has recommended settings and aliases (for recommended settings) 
* Folders inside settingFiles are versions of different settings, these are executed at the start of the application and used the start settingsToApply attribute to select which setting version to use. Currently there are 2 configuration files:
  ** initialHexapodSetup.yaml: Initial configuration of the hexapod
  ** tcpConfiguration.yaml: TCP Configuration for the ATHexapod controller 
     *** use endl for termination char

<footer>

LSST Data Management System Software
Copyright © 2008-2019 AURA/LSST.

This product includes software developed by the
LSST Project (http://www.lsst.org/) with contributions made at LSST partner
institutions.  The list of partner institutions is found at:
http://www.lsst.org/lsst/about/contributors .

Use and redistribution of this software is covered by the GNU Public License 
Version 3 (GPLv3) or later, as detailed below.  A copy of the GPLv3 is also 
available at  [GNU Licenses](http://www.gnu.org/licenses/).
</footer>

---
_**Ref:**_ [ATHexapod software user guide][athexapodguide]


[athexapodguide]: <https://confluence.lsstcorp.org/display/LTS/ATHexapod+software+user+guide#ATHexapodsoftwareuserguide-Howtoinstall>
[overview]: https://github.com/lsst-ts/ts_salobjATHexapod/blob/master/images/EUI-OverviewRedux.png "Overview"
[controls]: https://github.com/lsst-ts/ts_salobjATHexapod/blob/master/images/EUI-ControlsRedux.png "Controls"
[telemetry]: https://github.com/lsst-ts/ts_salobjATHexapod/blob/master/images/EUI-TelemRedux.png "Telemetry"

