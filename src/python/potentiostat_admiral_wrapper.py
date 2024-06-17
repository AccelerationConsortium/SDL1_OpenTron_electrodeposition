import sys
import os
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
            lambda deviceName: print("Device is Connected: %s" % deviceName)
        )
        self.tracker.connectToDeviceOnComPort(port)
        self.handler = self.tracker.getInstrumentHandler(instrument_name)

        self.get_data()
        # self.handler.activeDCDataReady.connect(
        #     lambda channel, data: print(
        #         "timestamp:",
        #         "{:.9f}".format(data.timestamp),
        #         "workingElectrodeVoltage: ",
        #         "{:.9f}".format(data.workingElectrodeVoltage),
        #     )
        # )
        # self.handler.activeACDataReady.connect(
        #     lambda channel, data: print(
        #         "frequency:",
        #         "{:.9f}".format(data.frequency),
        #         "absoluteImpedance: ",
        #         "{:.9f}".format(data.absoluteImpedance),
        #         "phaseAngle: ",
        #         "{:.9f}".format(data.phaseAngle),
        #     )
        # )
        self.handler.experimentNewElementStarting.connect(
            lambda channel, data: print(
                "New Node beginning:",
                data.stepName,
                "step number: ",
                data.stepNumber,
                " step sub : ",
                data.substepNumber,
            )
        )
        self.handler.experimentStopped.connect(
            lambda channel: print("Experiment Completed: %d" % channel)
        )

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
    def _add_experiment_element(self, element, repeat: int = 1):
        LOGGER.debug("_add_experiment_element: Appending element to experiment object")
        self.experiment.appendElement(element, repeat)

    def get_data(self):
        LOGGER.debug("get_data: Receiving AC data")
        self.handler.activeACDataReady.connect(
            lambda channel, data: print(
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

    # function to return eisPotentiostatic element
    def runEISPotentiostatic(
        self,
        startFrequency: float = 100000,
        endFrequency: float = 1000,
        stepsPerDecade: int = 10,
        voltageBias: float = 0.0,
        voltageAmplitude: float = 0.2,
        repeat_experiment: int = 1,
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
        # self.get_data()
        eisElement = AisEISPotentiostaticElement(
            startFrequency, endFrequency, stepsPerDecade, voltageBias, voltageAmplitude
        )

        self.experiment.appendElement(eisElement, repeat_experiment)

        # upload experiment to channel 1
        error = self.handler.uploadExperimentToChannel(
            self.channel_in_use, self.experiment
        )
        if error != 0:
            LOGGER.info(error.message())
            # return

        # start experiment on channel 1
        error = self.handler.startUploadedExperiment(self.channel_in_use)
        if error != 0:
            LOGGER.info(error.message())

        # Release the terminal and quit the Qt application
        self.app.quit()
