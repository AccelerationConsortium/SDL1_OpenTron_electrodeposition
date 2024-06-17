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
        instrument_name: str = "Puls1894",
        port: str = "COM5",
        channel_to_use: int = 0,
    ):
        """Initialize the Potentiostat Admiral Wrapper

        Args:
            instrument_name (str): The name of the instrument to connect to
            port (str): The port to connect to the device, eg. "COM5"
            channel_to_use (int): The channel on the potentiostat

        """

        self.app = QApplication()  # Initialize the Qt application
        self.tracker = AisDeviceTracker.Instance()  # Initialize the device tracker
        # self.data = pd.DataFrame(columns=["Timestamp", "Voltage [V]", "Current [A]"])

        # find device and report name
        self.tracker.newDeviceConnected.connect(
            lambda deviceName: print("Device is Connected: %s" % deviceName)
        )
        self.tracker.connectToDeviceOnComPort(port)
        self.experiment = AisExperiment()
        self.channel_in_use = channel_to_use
        self.handler = self.tracker.getInstrumentHandler(instrument_name)

    def _quitapp(self, channel: int):
        """Quit Qt the application and release the terminal

        Args:
            channel (int): The channel to quit the application on potentiostat
        """
        print("Experiment Completed: %d" % channel)
        self.app.quit()

    def _release_terminal(self):
        self.handler.experimentStopped.connect(self._quitapp)

    def __del__(self):
        self._release_terminal()

    # def get_data(self, timestamp, voltage, current):
    #     self.data = self.data.append(
    #         {"Timestamp": timestamp, "Voltage [V]": voltage, "Current [A]": current},
    #         ignore_index=True,
    #     )

    # send experiment to queue
    def _send_experiment(self, channelInUse: int):
        self.handler.uploadExperimentToChannel(channelInUse, self.experiment)

    # run experiment
    def _run_experiment(self, channelInUse: int):
        self.handler.startUploadedExperiment(channelInUse)

    # function to add element to experiment
    def _add_experiment_element(self, element):
        self.experiment.appendElement(element)

    def get_data(self):
        self.handler.activeACDataReady.connect(
            lambda channel, data: print(
                "timestamp: ,",
                "{:.9f}".format(data.timestamp),
                "frequency:",
                "{:.9f}".format(data.frequency),
                "absoluteImpedance: ",
                "{:.9f}".format(data.absoluteImpedance),
                "phaseAngle: ",
                "{:.9f}".format(data.phaseAngle),
            )
        )
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

    # function to return constantCurrent element
    def setConstantCurrent(self, holdAtCurrent, samplingInterval, duration):
        constantCurrent = AisConstantCurrentElement(
            holdAtCurrent, samplingInterval, duration
        )
        return constantCurrent

    # function to return constantPotential element
    def setConstantPotential(self, holdAtVoltage, samplingInterval, duration):
        constantPotential = AisConstantPotElement(
            holdAtVoltage, samplingInterval, duration
        )
        return constantPotential

    # function to return constantPower element
    def setConstantPower(self, isCharge, powerVal, duration, samplingInterval):
        constantPower = AisConstantPowerElement(
            isCharge, powerVal, duration, samplingInterval
        )
        return constantPower

    # function to return constantResistance element
    def setConstantResistance(self, resistanceVal, duration, samplingInterval):
        constantResistance = AisConstantResistanceElement(
            resistanceVal, duration, samplingInterval
        )
        return constantResistance

    # function to return CV element
    def setCyclicVoltammetry(
        self,
        startPotential: float = 0.0,  # V
        firstVoltageLimit: float = 0.1,  # V
        secondVoltageLimit: float = 0.0,  # V
        endVoltage: float = 0.0,  # V
        scanRate: float = 0.1,  # V/s
        samplingInterval: float = 0.1,  # s
    ):
        cyclicVoltammetry = AisCyclicVoltammetryElement(
            startPotential,
            firstVoltageLimit,
            secondVoltageLimit,
            endVoltage,
            scanRate,
            samplingInterval,
        )

        # Add the element to the experiment
        self._add_experiment_element(cyclicVoltammetry)
        self._send_experiment(self.channel_in_use)
        self._run_experiment(self.channel_in_use)
        self._release_terminal()

    # function to return dcCurrentSweep element
    def setDCCurrentSweep(self, startCurrent, endCurrent, scanRate, samplingInterval):
        dcCurrentSweep = AisDCCurrentSweepElement(
            startCurrent, endCurrent, scanRate, samplingInterval
        )
        return dcCurrentSweep

    # function to return dcPotentialSweep element
    def setDCPotentialSweep(
        self, startPotential, endPotential, scanRate, samplingInterval
    ):
        dcPotentialSweep = AisDCPotentialSweepElement(
            startPotential, endPotential, scanRate, samplingInterval
        )
        return dcPotentialSweep

    # function to return diffPulse element
    def setDiffPulse(
        self,
        startPotential,
        endPotential,
        potentialStep,
        pulseHeight,
        pulseWidth,
        pulsePeriod,
    ):
        diffPulse = AisDiffPulseVoltammetryElement(
            startPotential,
            endPotential,
            potentialStep,
            pulseHeight,
            pulseWidth,
            pulsePeriod,
        )
        return diffPulse

    # function to return normalPulse element

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
