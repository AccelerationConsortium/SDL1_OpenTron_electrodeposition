import requests
import json
import logging

LOGGER = logging.getLogger(__name__)

class opentronsClient:
    '''
    each object will represent a single experiment
    '''

    def __init__(self,
                 strRobotIP: str,
                 dicHeaders: dict = {"opentrons-version": "3"},):
        '''
        initializes the object with the robot IP and headers

        arguments
        ----------
        strRobotIP: str
            the IP address of the robot

        dicHeaders: dict
            the headers to be used in the requests

        returns
        ----------
        None
        '''
        self.robotIP = strRobotIP
        self.headers = dicHeaders
        self.runID = None
        self.commandURL = None

        # *** NEED TO ADD FIXED TRASH TO LABWARE BY DEFAULT ***
        self.labware = {"fixed-trash": {'id': 'fixed-trash', 'slot': 12}}

        self.pipettes = {}
        self._initalizeRun()

    def _initalizeRun(self):
        '''
        creates a new blank run on the opentrons with command endpoints
        
        arguments
        ----------
        None

        returns
        ----------
        None
        '''

        strRunURL = f"http://{self.robotIP}:31950/runs"
        # create a new run
        response = requests.post(url=strRunURL,
                                 headers=self.headers
                                 )

        if response.status_code == 201:
            dicResponse = json.loads(response.text)
            # get the run ID
            self.runID = dicResponse['data']['id']
            # setup command endpoints
            self.commandURL = strRunURL + f"/{self.runID}/commands"

            # LOG - info
            LOGGER.info(f"New run created with ID: {self.runID}")
            LOGGER.info(f"Command URL: {self.commandURL}")

        else:
            raise Exception(f"Failed to create a new run.\nError code: {response.status_code}\n Error message: {response.text}")

    def loadLabware(self,
                    intSlot: int,
                    strLabwareName: str,
                    strNamespace: str = "opentrons",
                    intVersion: int = 1,
                    strIntent: str = "setup"):
        '''
        loads labware onto the robot

        arguments
        ----------
        intSlot: int
            the slot number where the labware is to be loaded

        strLabwareName: str
            the name of the labware to be loaded
            
        strNamespace: str
            the namespace of the labware to be loaded
            default: "opentrons"

        intVersion: int
            the version of the labware to be loaded
            default: 1

        strIntent: str
            the intent of the command
            default: "setup"

        returns
        ----------
        None
        '''

        dicCommand = {
            "data": {
                "commandType": "loadLabware",
                "params": {
                    "location": {"slotName": str(intSlot)},
                    "loadName": strLabwareName,
                    "namespace": strNamespace,
                    "version": str(intVersion)
                },
                "intent": strIntent
            }
        }

        strCommand = json.dumps(dicCommand)

        # LOG - info
        LOGGER.info(f"Loading labware: {strLabwareName} in slot: {intSlot}")
        # LOG - debug
        LOGGER.debug(f"Command: {strCommand}")

        response = requests.post(
            url = self.commandURL,
            headers = self.headers,
            params = {"waitUntilComplete": True},
            data = strCommand
        )

        # LOG - debug
        LOGGER.debug(f"Response: {response.text}")

        if response.status_code == 201:
            dicResponse = json.loads(response.text)
            strLabwareID = dicResponse['data']['result']['labwareId']
            strLabwareIdentifier_temp = strLabwareName + "_" + str(intSlot)
            self.labware[strLabwareIdentifier_temp] = {"id": strLabwareID, "slot": intSlot}
            # LOG - info
            LOGGER.info(f"Labware loaded with name: {strLabwareName} and ID: {strLabwareID}")
        else:
            raise Exception(f"Failed to load labware.\nError code: {response.status_code}\n Error message: {response.text}")

    def loadCustomLabware(self,
                          dicLabware: dict,
                          intSlot: int,
                          ):
        '''
        loads custom labware onto the robot

        arguments
        ----------
        dicLabware: dict
            the JSON object of the custom labware to be loaded (directly from opentrons labware definitions)

        intSlot: int
            the slot number where the labware is to be loaded

        strLabwareID: str
            the ID of the labware to be loaded - to be used for loading the same labware multiple times
            default: None

        returns
        ----------
        None
        '''

        dicCommand = {'data' : dicLabware}

        strCommand = json.dumps(dicCommand)

        # LOG - info
        LOGGER.info(f"Loading custom labware: {dicLabware['parameters']['loadName']} in slot: {intSlot}")
        # LOG - debug
        LOGGER.debug(f"Command: {strCommand}")

        response = requests.post(
            url = f"http://{self.robotIP}:31950/runs/{self.runID}/labware_definitions",
            headers = self.headers,
            data = strCommand
        )

        # LOG - debug
        LOGGER.debug(f"Response: {response.text}")

        if response.status_code == 201:
            # LOG - info
            LOGGER.info(f"Custome labware {dicLabware['parameters']['loadName']} loaded in slot: {intSlot} successfully.")
            # load the labware
            self.loadLabware(intSlot = intSlot,
                             strLabwareName = dicLabware['parameters']['loadName'],
                             strNamespace = dicLabware['namespace'],
                             intVersion = dicLabware['version'],
                             strIntent = "setup"
                             )
        else:
            raise Exception(
                f"Failed to load custom labware.\nError code: {response.status_code}\n Error message: {response.text}"
            )

    # *** WIP ***
    def loadLiquid(self,
                   strLiquidName: str,):
        pass

    def loadPipette(self,
                    strPipetteName: str,
                    strMount: str):
        '''
        loads a pipette onto the robot

        arguments
        ----------
        strPipetteName: str
            the name of the pipette to be loaded

        strMount: str
            the mount where the pipette is to be loaded

        returns
        ----------
        None
        '''

        dicCommand = {
            "data": {
                "commandType": "loadPipette",
                "params": {
                    "pipetteName": strPipetteName,
                    "mount": strMount
                },
                "intent": "setup"
            }
        }

        strCommand = json.dumps(dicCommand)

        # LOG - info
        LOGGER.info(f"Loading pipette: {strPipetteName} on mount: {strMount}")
        # LOG - debug
        LOGGER.debug(f"Command: {strCommand}")

        response = requests.post(
            url = self.commandURL,
            headers = self.headers,
            params = {"waitUntilComplete": True},
            data = strCommand
        )

        # LOG - debug
        LOGGER.debug(f"Response: {response.text}")

        if response.status_code == 201:
            dicResponse = json.loads(response.text)
            strPipetteID = dicResponse['data']['result']['pipetteId']
            self.pipettes[strPipetteName] = {"id": strPipetteID, "mount": strMount}
            # LOG - info
            LOGGER.info(f"Pipette loaded with name: {strPipetteName} and ID: {strPipetteID}")
        else:
            raise Exception(
                f"Failed to load pipette.\nError code: {response.status_code}\n Error message: {response.text}"
            )

    def homeRobot(self):
        '''
        homes the robot - this should be done before doing any other movements of the robot per instance but need to implement this***

        arguments
        ----------
        None

        returns
        ----------
        None
        '''

        strCommand = json.dumps({"target": "robot"})

        # LOG - info
        LOGGER.info(f"Homing the robot")
        # LOG - debug
        LOGGER.debug(f"Command: {strCommand}")

        response = requests.post(
            url = f"http://{self.robotIP}:31950/robot/home",
            headers = self.headers,
            data = strCommand
        )

        # LOG - debug
        LOGGER.debug(f"Response: {response.text}")
        if response.status_code == 200:
            # LOG - info
            LOGGER.info(f"Robot homed successfully.")
        else:
            raise Exception(
                f"Failed to home the robot.\nError code: {response.status_code}\n Error message: {response.text}"
            )

    def pickUpTip(self,
                  strLabwareName: str,
                  strPipetteName: str,
                  strOffsetStart: str = "top",
                  strOffsetX: float = 0,
                  strOffsetY: float = 0,
                  strOffsetZ: float = 0,
                  strWellName: str = "A1",
                  strIntent: str = "setup"
                  ):
        '''
        picks up a tip from a labware

        arguments
        ----------
        strLabwareName: str
            the name of the labware from which the tip is to be picked up

        strWellName: str
            the name of the well from which the tip is to be picked up

        returns
        ----------
        None
        '''

        # *** WIP ***
        # build in some check to see if the tip is already picked up

        dicCommand = {
            "data": {
                "commandType": "pickUpTip",
                "params": {
                    "labwareId": self.labware[strLabwareName]["id"],
                    "wellName": strWellName,
                    "wellLocation": {
                        "origin": strOffsetStart,
                        "offset": {"x": strOffsetX, "y": strOffsetY, "z": strOffsetZ}
                        },
                    "pipetteId": self.pipettes[strPipetteName]["id"],
                },
                "intent": strIntent
            }
        }

        jsonCommand = json.dumps(dicCommand)

        # LOG - info
        LOGGER.info(f"Picking up tip from labware: {strLabwareName}")
        # LOG - debug
        LOGGER.debug(f"Command: {jsonCommand}")

        jsonResponse = requests.post(
            url = self.commandURL,
            headers = self.headers,
            params = {"waitUntilComplete": True},
            data = jsonCommand
        )

        # LOG - debug
        LOGGER.debug(f"Response: {jsonResponse.text}")

        if jsonResponse.status_code == 201:
            # LOG - info
            LOGGER.info(f"Tip picked up from labware: {strLabwareName}, well: {strWellName}")

        else:
            raise Exception(f"Failed to pick up tip.\nError code: {jsonResponse.status_code}\n Error message: {jsonResponse.text}")

    def dropTip(self,
                strPipetteName: str,
                strLabwareName: str = "fixed-trash",
                strWellName: str = "A1",
                strOffsetStart: str = "center",
                strOffsetX: int = 0,
                strOffsetY: int = 0,
                strOffsetZ: int = 0,
                boolHomeAfter: bool = False,
                boolAlternateDropLocation: bool = False,
                strIntent: str = "setup",
                ):
        '''
        drops a tip into a labware

        arguments
        ----------
        strPipetteName: str
            the name of the pipette from which the tip is to be dropped

        strLabwareName: str
            the name of the labware into which the tip is to be dropped
            default: "fixed-trash"

        strWellName: str
            the name of the well into which the tip is to be dropped
            default: "A1"

        strOffsetStart: str
            the starting point of the drop
            default: "center"

        strOffsetX: int
            the x offset of the drop
            default: 0

        strOffsetY: int
            the y offset of the drop
            default: 0

        strOffsetZ: int
            the z offset of the drop
            default: 0

        boolHomeAfter: bool
            whether the robot should home after the drop
            default: False

        boolAlternateDropLocation: bool
            whether the robot should use an alternate drop location
            default: False

        strIntent: str
            the intent of the command
            default: "setup"
        '''

        # *** BUILD IN CHECK TO SEE IF THERE IS A TIP TO DROP ***

        # make command dictionary
        dicCommand = {
            "data": {
                "commandType": "dropTip",
                "params": {
                    "pipetteId": self.pipettes[strPipetteName]["id"],
                    "labwareId": self.labware[strLabwareName]["id"],
                    "wellName": strWellName,
                    "wellLocation": {
                        "origin": strOffsetStart,
                        "offset": {"x": strOffsetX, "y": strOffsetY, "z": strOffsetZ}
                    },
                    "homeAfter": boolHomeAfter,
                    "alternateDropLocation": boolAlternateDropLocation
                },
                "intent": strIntent
            }
        }

        # dump to string
        strCommand = json.dumps(dicCommand)

        # LOG - info
        LOGGER.info(f"Dropping tip into labware: {strLabwareName}")
        # LOG - debug
        LOGGER.debug(f"Command: {strCommand}")

        # make request
        response = requests.post(
            url = self.commandURL,
            headers = self.headers,
            params = {"waitUntilComplete": True},
            data = strCommand
        )

        # LOG - debug
        LOGGER.debug(f"Response: {response.text}")

        if response.status_code == 201:
            # LOG - info
            LOGGER.info(f"Tip dropped into labware: {strLabwareName}, well: {strWellName}")
        else:
            raise Exception(f"Failed to drop tip.\nError code: {response.status_code}\n Error message: {response.text}")

    def aspirate(self,
                 strLabwareName: str,
                 strWellName: str,
                 strPipetteName: str,
                 intVolume: int,                        # uL
                 fltFlowRate: float = 818.343,          # uL/s -- need to check this
                 strOffsetStart: str = "top",
                 strOffsetX: int = 0,
                 strOffsetY: int = 0,
                 strOffsetZ: int = 0,
                 strIntent: str = "setup"
                 ):
        '''
        aspirates liquid from a well

        arguments
        ----------
        strLabwareName: str
            the name of the labware from which the liquid is to be aspirated

        strWellName: str
            the name of the well from which the liquid is to be aspirated

        strPipetteName: str
            the name of the pipette to be used for aspiration

        intVolume: int  
            the volume of liquid to be aspirated
            units: uL

        intFlowRate: int
            the flow rate of the aspiration
            units: uL/s
            default: 7

        strOffsetStart: str
            the starting point of the aspiration
            default: "top"

        strOffsetX: int
            the x offset of the aspiration
            default: 0

        strOffsetY: int
            the y offset of the aspiration
            default: 0

        strOffsetZ: int
            the z offset of the aspiration
            default: 0

        strIntent: str
            the intent of the command
            default: setup

        returns
        ----------
        None
        '''

        # make command dictionary
        dicCommand = {
            "data": {
                "commandType": "aspirate",
                "params": {
                    "labwareId": self.labware[strLabwareName]["id"],
                    "wellName": strWellName,
                    "wellLocation": {
                        "origin": strOffsetStart,
                        "offset": {"x": strOffsetX, "y": strOffsetY, "z": strOffsetZ}
                    },
                    "flowRate": str(fltFlowRate),
                    "volume": str(intVolume),
                    "pipetteId": self.pipettes[strPipetteName]["id"]
                },
                "intent": strIntent
            }
        }

        # dump to string
        strCommand = json.dumps(dicCommand)

        # LOG - info
        LOGGER.info(f"Aspirating from labware: {strLabwareName}, well: {strWellName}")
        # LOG - debug
        LOGGER.debug(f"Command: {strCommand}")

        # make request
        response = requests.post(
            url = self.commandURL,
            headers = self.headers,
            params = {"waitUntilComplete": True},
            data = strCommand
        )

        # LOG - debug
        LOGGER.debug(f"Response: {response.text}")

        if response.status_code == 201:
            # LOG - info
            LOGGER.info(f"Aspiration successful.")
        else:
            raise Exception(
                f"Failed to aspirate.\nError code: {response.status_code}\n Error message: {response.text}"
            )

    def dispense(self,
                 strLabwareName: str,
                 strWellName: str,
                 strPipetteName: str,
                 intVolume: int,                        # uL
                 fltFlowRate: float = 818.343,          # uL/s -- need to check this
                 strOffsetStart: str = "top",
                 strOffsetX: int = 0,
                 strOffsetY: int = 0,
                 strOffsetZ: int = 0,
                 strIntent: str = "setup"
                 ):
        '''
        dispenses liquid into a well

        arguments
        ----------
        strLabwareName: str
            the name of the labware from which the liquid is to be aspirated

        strWellName: str
            the name of the well from which the liquid is to be aspirated

         strPipetteName: str
            the name of the pipette to be used for aspiration

        intVolume: int  
            the volume of liquid to be aspirated
            units: uL

        intFlowRate: int
            the flow rate of the aspiration
            units: uL/s
            default: 7

        strOffsetStart: str
            the starting point of the aspiration
            default: "top"

        strOffsetX: int
            the x offset of the aspiration
            default: 0

        strOffsetY: int
            the y offset of the aspiration
            default: 0

        strOffsetZ: int
            the z offset of the aspiration
            default: 0

        strIntent: str
            the intent of the command
            default: setup

        returns
        ----------
        None
        '''

        # make command dictionary
        dicCommand = {
            "data": {
                "commandType": "dispense",
                "params": {
                    "labwareId": self.labware[strLabwareName]["id"],
                    "wellName": strWellName,
                    "wellLocation": {
                        "origin": strOffsetStart,
                        "offset": {"x": strOffsetX, "y": strOffsetY, "z": strOffsetZ}
                    },
                    "flowRate": fltFlowRate,
                    "volume": intVolume,
                    "pipetteId": self.pipettes[strPipetteName]["id"]
                },
                "intent": strIntent
            }
        }

        # dump to string
        strCommand = json.dumps(dicCommand)

        # LOG - info
        LOGGER.info(f"Dispensing into labware: {strLabwareName}, well: {strWellName}")
        # LOG - debug
        LOGGER.debug(f"Command: {strCommand}")

        # make request
        response = requests.post(
            url = self.commandURL,
            headers = self.headers,
            params = {"waitUntilComplete": True},
            data = strCommand
        )

        # LOG - debug
        LOGGER.debug(f"Response: {response.text}")

        if response.status_code == 201:
            # LOG - info
            LOGGER.info("Dispense successful.")
        else:
            raise Exception(f"Failed to dispense.\nError code: {response.status_code}\n Error message: {response.text}")

    def moveToWell(self,
                   strLabwareName: str,
                   strWellName: str,
                   strPipetteName: str,
                   strOffsetStart: str = "top",
                   intOffsetX: int = 0,
                   intOffsetY: int = 0,
                   intOffsetZ: int = 0,
                   strIntent: str = "setup"
                   ):
        '''
        moves the pipette to a well

        arguments
        ----------
        strLabwareName: str
            the name of the labware to which the pipette is to be moved

        strWellName: str
            the name of the well to which the pipette is to be moved

        strPipetteName: str
            the name of the pipette to be moved

        strOffsetStart: str
            the starting point of the move
            default: "top"

        intOffsetX: int
            the x offset of the move
            default: 0

        intOffsetY: int
            the y offset of the move
            default: 0

        intOffsetZ: int
            the z offset of the move
            default: 0

        strIntent: str
            the intent of the command
            default: setup  

        returns
        ----------
        None
        '''

        # make command dictionary
        dicCommand = {
            "data": {
                "commandType": "moveToWell",
                "params": {
                    "labwareId": self.labware[strLabwareName]["id"],
                    "wellName": strWellName,
                    "wellLocation": {
                        "origin": strOffsetStart,
                        "offset": {"x": intOffsetX, "y": intOffsetY, "z": intOffsetZ},
                    },
                    "pipetteId": self.pipettes[strPipetteName]["id"],
                },
                "intent": strIntent,
            }
        }

        # dump to string
        strCommand = json.dumps(dicCommand)

        # LOG - info
        LOGGER.info(f"Moving pipette to labware: {strLabwareName}, well: {strWellName}")
        # LOG - debug
        LOGGER.debug(f"Command: {strCommand}")

        # make request
        response = requests.post(
            url = self.commandURL,
            headers = self.headers,
            params = {"waitUntilComplete": True},
            data = strCommand
        )

        # LOG - debug
        LOGGER.debug(f"Response: {response.text}")

        if response.status_code == 201:
            # LOG - info
            LOGGER.info("Move successful.")
        else:
            raise Exception(
                f"Failed to move pipette.\nError code: {response.status_code}\n Error message: {response.text}"
            )

    def addLabwareOffsets(self,
                          ):
        pass

    def turnLightsOn(self):
        pass

    def turnLightsOff(self):
        pass

    """
    TODO LIST 
    -----------

    ADD CHECK TO SEE WELL IS VALID FOR ASPIRATION/DISPENSE

    ADD ADDITIONAL CHECK FOR ALL REQUESTS -  status == FAILED
        it is possible for the robot to return a response (ie. status_code == 201) but the command to fail

    FIGURE OUT FIXED TRASH

    LOAD LIQUID

    """
