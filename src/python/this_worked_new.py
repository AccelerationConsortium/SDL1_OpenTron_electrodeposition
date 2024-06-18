from PySide2.QtWidgets import QApplication
from SquidstatPyLibrary import (
    AisDeviceTracker,
    AisExperiment,
    AisEISPotentiostaticElement,
    AisCyclicVoltammetryElement,
)
import pandas as pd


class AdmiralWrapper:
    def __init__(self):
        self.app = QApplication()
        self.tracker = AisDeviceTracker.Instance()
        self.handler = None
        self.channel = 0

        self.ac_data_list = pd.DataFrame(
            columns=[
                "Timestamp",
                "Frequency [Hz]",
                "Absolute Impedance",
                "Phase Angle",
                "Real Impedance",
                "Imaginary Impedance",
                "Total Harmonic Distortion",
                "Number of Cycles",
                "Working electrode DC Voltage [V]",
                "DC Current [A]",
                "Current Amplitude",
                "Voltage Amplitude",
            ]
        )
        self.dc_data_list = pd.DataFrame(
            columns=[
                "Timestamp",
                "Working Electrode Voltage [V]",
                "Working Electrode Current [A]",
                "Temperature [C]",
            ]
        )
        self.new_element_list = pd.DataFrame(
            columns=["Step Name", "Step Number", "Substep Number"]
        )

    def handle_dc_data(self, channel, data):
        # Use concat to append the data to the dataframe
        self.dc_data_list = pd.concat(
            [
                self.dc_data_list,
                pd.DataFrame(
                    {
                        "Timestamp": [data.timestamp],
                        "Working Electrode Voltage [V]": [data.workingElectrodeVoltage],
                        "Working Electrode Current [A]": [data.current],
                        "Temperature [C]": [data.temperature],
                    }
                ),
            ]
        )

    def handle_ac_data(self, channel, data):
        # Use concat to append the data to the dataframe
        self.ac_data_list = pd.concat(
            [
                self.ac_data_list,
                pd.DataFrame(
                    {
                        "Timestamp": [data.timestamp],
                        "Frequency [Hz]": [data.frequency],
                        "Absolute Impedance": [data.absoluteImpedance],
                        "Phase Angle": [data.phaseAngle],
                        "Real Impedance": [data.realImpedance],
                        "Imaginary Impedance": [data.imagImpedance],
                        "Total Harmonic Distortion": [data.totalHarmonicDistortion],
                        "Number of Cycles": [data.numberOfCycles],
                        "Working electrode DC Voltage [V]": [
                            data.workingElectrodeDCVoltage
                        ],
                        "DC Current [A]": [data.DCCurrent],
                        "Current Amplitude": [data.currentAmplitude],
                        "Voltage Amplitude": [data.voltageAmplitude],
                    }
                ),
            ]
        )

    def handle_new_element(self, channel, data):
        # Use concat instead of append to append the data to the dataframe
        self.new_element_list = pd.concat(
            [
                self.new_element_list,
                pd.DataFrame(
                    {
                        "Step Name": [data.stepName],
                        "Step Number": [data.stepNumber],
                        "Substep Number": [data.substepNumber],
                    }
                ),
            ]
        )

    def on_device_connected(self, device_name):
        print("Device is Connected: %s" % device_name)

    def handle_experiment_stopped(self, channel):
        print("Experiment Completed: %d" % channel)
        self.app.quit()

    def connect_to_device(self, port):
        self.tracker.newDeviceConnected.connect(self.on_device_connected)
        self.tracker.connectToDeviceOnComPort(port)
        self.handler = self.tracker.getInstrumentHandler("Plus1894")

    def setup_data_handlers(self):
        self.handler.activeDCDataReady.connect(self.handle_dc_data)
        self.handler.activeACDataReady.connect(self.handle_ac_data)
        self.handler.experimentNewElementStarting.connect(self.handle_new_element)
        self.handler.experimentStopped.connect(self.handle_experiment_stopped)

    def upload_experiment(self, experiment):
        """Internal function, to be run after the element (measurement) has been appended to the experiment"""
        error = self.handler.uploadExperimentToChannel(self.channel, experiment)
        if error != 0:
            print(error.message())

    def start_experiment(self):
        """Internal function, to be run after upload_experiment"""
        error = self.handler.startUploadedExperiment(self.channel)
        if error != 0:
            print(error.message())

    def run_potentiostaticEIS(
        self,
        start_frequency: float = 10000,
        end_frequency: float = 1000,
        points_per_decade: int = 10,
        voltage_bias: float = 0.0,
        voltage_amplitude: float = 0.1,
        number_of_runs: int = 1,
    ):
        """Perform an potentiostatic EIS experiment on the potentiostat

        Args:
            start_frequency (float): The start frequency of the EIS experiment
            end_frequency (float): The end frequency of the EIS experiment
            points_per_decade (int): The number of points per decade
            voltage_bias (float): The bias voltage of the EIS experiment
            voltage_amplitude (float): The amplitude of the voltage signal
        """
        experiment = AisExperiment()
        element = AisEISPotentiostaticElement(
            start_frequency,
            end_frequency,
            points_per_decade,
            voltage_bias,
            voltage_amplitude,
        )
        experiment.appendElement(element, number_of_runs)
        self.upload_experiment(experiment)
        self.start_experiment()

    def run_CV(
        self,
        startPotential: float = 0,
        firstVoltageLimit: float = 0.6,
        secondVoltageLimit: float = 0,
        endVoltage: float = 0,
        scanRate: float = 0.1,
        samplingInterval: float = 0.001,
        number_of_runs=1,
    ):
        """Perform a cyclic voltammetry experiment on the potentiostat

        Args:
            startPotential (float): The start potential of the cyclic
                voltammetry experiment
            firstVoltageLimit (float): The first voltage limit of the cyclic
                voltammetry experiment
            secondVoltageLimit (float): The second voltage limit of the cyclic
                voltammetry experiment
            endVoltage (float): The end voltage of the cyclic voltammetry
                experiment
            scanRate (float): The scan rate of the cyclic voltammetry
                experiment
            samplingInterval (float): The sampling interval of the cyclic
                voltammetry experiment
        """
        experiment = AisExperiment()
        element = AisCyclicVoltammetryElement(
            startPotential,
            firstVoltageLimit,
            secondVoltageLimit,
            endVoltage,
            scanRate,
            samplingInterval,
        )
        experiment.appendElement(element, number_of_runs)
        self.upload_experiment(experiment)
        self.start_experiment()


eis_measurement = AdmiralWrapper()
eis_measurement.connect_to_device("COM5")
eis_measurement.setup_data_handlers()
eis_measurement.run_potentiostaticEIS()
eis_measurement.app.exec_()

print("DC Data:")
print(eis_measurement.dc_data_list)
print("AC Data:")
print(eis_measurement.ac_data_list)
