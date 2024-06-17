import sys
import logging
import SquidstatPyLibrary as SquidLib
from SquidstatPyLibrary import AisCyclicVoltammetryElement
from SquidstatPyLibrary import AisSquareWaveVoltammetryElement
from SquidstatPyLibrary import AisConstantCurrentElement
from SquidstatPyLibrary import AisConstantPotElement
from SquidstatPyLibrary import AisConstantPowerElement
from SquidstatPyLibrary import AisConstantResistanceElement
from SquidstatPyLibrary import AisDCCurrentSweepElement
from SquidstatPyLibrary import AisDCPotentialSweepElement
from SquidstatPyLibrary import AisDiffPulseVoltammetryElement
from SquidstatPyLibrary import AisNormalPulseVoltammetryElement
from SquidstatPyLibrary import AisEISGalvanostaticElement
from SquidstatPyLibrary import AisEISPotentiostaticElement
from SquidstatPyLibrary import AisOpenCircuitElement
from SquidstatPyLibrary import AisDeviceTracker
from SquidstatPyLibrary import AisCompRange
from SquidstatPyLibrary import AisDCData
from SquidstatPyLibrary import AisACData
from SquidstatPyLibrary import AisExperimentNode
from SquidstatPyLibrary import AisErrorCode
from SquidstatPyLibrary import AisExperiment
from SquidstatPyLibrary import AisInstrumentHandler
from PySide2.QtWidgets import QApplication
# import pandas as pd

LOGGER = logging.getLogger(__name__)


class PotentiostatAdmiralWrapper():
    def __init__(
        self,
        instrument_name: str = "Plus1894",
        port: str = "COM5",
        channel_to_use: int = 0,
    ):
        """Initialize the Potentiostat Admiral Wrapper

        Args:
            instrument_name (str): The name of the instrument to connect to
            port (str): The port to connect to the device, eg. "COM5"
            channel_to_use (int): The channel on the potentiostat

        """
        LOGGER.debug("__init__: Initializing Potentiostat Admiral Wrapper")

        self.app = QApplication()  # Initialize the Qt application
        self.tracker = AisDeviceTracker.Instance()  # Initialize the device tracker

        # find device and report name
        self.tracker.newDeviceConnected.connect(
            lambda deviceName: LOGGER.info("Device is Connected: %s" % deviceName)
        )
        self.tracker.connectToDeviceOnComPort(port)
        self.handler = self.tracker.getInstrumentHandler(instrument_name)

        self.experiment = AisExperiment()
        self.channel_in_use = channel_to_use

    def _quitapp(self, channel: int):
        """Quit Qt the application and release the terminal

        Args:
            channel (int): The channel to quit the application on potentiostat
        """
        LOGGER.debug("_quitapp: Quitting the Qt application")
        self.app.quit()
        LOGGER.info("_quitapp: Measurement Completed: %d" % channel)

    def _release_terminal(self):
        LOGGER.debug("_release_terminal: Releasing terminal")
        self.handler.experimentStopped.connect(self._quitapp)

    def __del__(self):
        LOGGER.debug("__del__: Deleting Potentiostat Admiral Wrapper")
        self._release_terminal()

    # send experiment to queue
    def _send_experiment(self, channelInUse: int):
        LOGGER.debug("_send_experiment: Sending experiment to queue")
        self.handler.uploadExperimentToChannel(channelInUse, self.experiment)

    # run experiment
    def _run_experiment(self, channelInUse: int):
        LOGGER.debug("_run_experiment: Running experiment")
        self.handler.startUploadedExperiment(channelInUse)

    # function to add element to experiment
    def _add_experiment_element(self, element):
        LOGGER.debug("_add_experiment_element: Appending element to experiment object")
        self.experiment.appendElement(element)

    def get_data(self):
        LOGGER.debug("get_data: Receiving AC data")
        self.handler.activeACDataReady.connect(
            lambda channel, data: LOGGER.debug(
                "Timestamp: ,",
                "{:.9f}".format(data.timestamp),
                "Frequency [Hz]:",
                "{:.9f}".format(data.frequency),
                "Absolute Impedance: ",
                "{:.9f}".format(data.absoluteImpedance),
                "Phase Angle: ",
                "{:.9f}".format(data.phaseAngle),
                "Real Impedance: ",
                "{:.9f}".format(data.realImpedance),
                "Imaginary Impedance: ",
                "{:.9f}".format(data.imagImpedance),
                "Total Harmonic Distortion: ",
                "{:.9f}".format(data.totalHarmonicDistortion),
                "Number of Cycles: ",
                "{:.9f}".format(data.numberOfCycles),
                "Working electrode DC Voltage: ",
                "{:.9f}".format(data.workingElectrodeDCVoltage),
                "DC Current: ",
                "{:.9f}".format(data.DCCurrent),
                "Current Amplitude: ",
                "{:.9f}".format(data.currentAmplitude),
                "Voltage Amplitude: ",
                "{:.9f}".format(data.voltageAmplitude),
            )
        )

        LOGGER.debug("get_data: Receiving DC data")
        self.handler.activeDCDataReady.connect(
            lambda channel, data: print(
                "timestamp: ,",
                "{:.9f}".format(data.timestamp),
                ", workingElectrodeVoltage: ,",
                "{:.9f}".format(data.workingElectrodeVoltage),
                ", workingElectrodeCurrent: ,",
                "{:.9f}".format(data.current),
                ", Temperature, ",
                "{:.2f}".format(data.temperature),
            )
        )

        self.handler.activeDCDataReady.connect(
            lambda channel, data: print(
                "timestamp",
                "{:.9f}".format(data.timestamp),
                "workingElectrodeVoltage",
                "{:.9f}".format(data.workingElectrodeVoltage),
                "workingElectrodeCurrent:",
                "{:.9f}".format(data.current),
                "Temperature",
                "{:.2f}".format(data.temperature),
            )
        )
        print("Data Received")

    # function to return eisPotentiostatic element
    def runEISPotentiostatic(
        self,
        startFrequency: float = 100000,
        endFrequency: float = 1000,
        stepsPerDecade: int = 10,
        voltageBias: float = 0.0,
        voltageAmplitude: float = 0.2,
    ):
        """Set the experiment to EIS Potentiostatic

        Args:
            startFrequency (float): The start frequency in Hz
            endFrequency (float): The end frequency in Hz
            stepsPerDecade (int): The number of steps per decade
            voltageBias (float): The voltage bias
            voltageAmplitude (float): The voltage amplitude
        """
        LOGGER.info("Running EIS Potiontiostatic")
        eisPotentiostatic = AisEISPotentiostaticElement(
            startFrequency, endFrequency, stepsPerDecade, voltageBias, voltageAmplitude
        )

        # Add the element to the experiment
        self._add_experiment_element(eisPotentiostatic)

        # Send the experiment to the potentiostat
        self._send_experiment(self.channel_in_use)

        # Run the experiment
        self._run_experiment(self.channel_in_use)

        # Receive the data
        self.get_data()

        # Release the terminal and quit the Qt application
        self._quitapp(self.channel_in_use)
