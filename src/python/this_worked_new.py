from PySide2.QtWidgets import QApplication
from SquidstatPyLibrary import (
    AisDeviceTracker,
    AisExperiment,
    AisEISPotentiostaticElement,
    AisCyclicVoltammetryElement,
)
import pandas as pd
import time
import warnings

# Suppress FutureWarning messages from Pandas
warnings.simplefilter(action='ignore', category=FutureWarning)


class AdmiralWrapper:
    def __init__(self, port="COM5", instrument_name="Plus1894"):
        """ Initialize the AdmiralWrapper class. This class is used to interface with the Admiral potentiostat.
        
        Args:
            port (str, optional): The COM port to which the potentiostat is connected. Defaults to "COM5".
            instrument_name (str, optional): The name of the instrument. Defaults to "Plus1894".
        """

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
        self.connect_to_device(port=port, instrument_name=instrument_name)
        self.setup_data_handlers()

    def __del__(self):
        """Close the experiment on the potentiostat and release the Qt application. Remember to call get_data() before calling this function to retrieve the data."""
        self.app.quit()
        time.sleep(1)
        
    def get_data(self):
        """Return the AC and DC data as pandas dataframes. If no data is available, return None for the respective dataframe.
        
        Returns:
            [pd.DataFrame, pd.DataFrame]: A list containing the two AC data and the DC data pandas dataframes.
        """
        print("Returning data")
        if self.ac_data_list.empty is True:
            print("No AC data available \n")
            return None, self.dc_data_list
        elif self.dc_data_list.empty is True:
            print("No DC data available \n")
            return self.ac_data_list, None
        else:
            print("")
            return self.ac_data_list, self.dc_data_list
        
    def clear_data(self):
        """Clear the AC and DC data dataframes."""
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
        # self.new_element_list = pd.DataFrame(
        #     columns=["Step Name", "Step Number", "Substep Number"]
        # )
        time.sleep(1)

    def handle_dc_data(self, channel, data):
        if data.timestamp is not None:
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
        if data.timestamp is not None:
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
        print(f"Device is connected as: {device_name} \nPlease use this name when loading the AdmiralWrapper.")


    def handle_experiment_stopped(self, channel):
        print("Experiment completed on channel: %d" % channel)
        self.app.quit()

    def connect_to_device(self, port, instrument_name="Plus1894"):
        self.tracker.newDeviceConnected.connect(self.on_device_connected)
        self.tracker.connectToDeviceOnComPort(port)
        self.handler = self.tracker.getInstrumentHandler(instrument_name)

    def setup_data_handlers(self):
        self.handler.activeDCDataReady.connect(self.handle_dc_data)
        self.handler.activeACDataReady.connect(self.handle_ac_data)
        self.handler.experimentNewElementStarting.connect(self.handle_new_element)
        self.handler.experimentStopped.connect(self.handle_experiment_stopped)

    def upload_experiment(self, experiment):
        """Internal function, to be run after the element (measurement) has been appended to the experiment"""
        print("Uploading experiment")
        error = self.handler.uploadExperimentToChannel(self.channel, experiment)
        if error != 0:
            print(error.message())

    def start_experiment(self):
        """Internal function, to be run after upload_experiment"""
        print("Setting potentiostat in start experiment modus")
        error = self.handler.startUploadedExperiment(self.channel)
        if error != 0:
            print(error.message())

    def setup_potentiostaticEIS(
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

        print("\n*** Preparing EIS experiment")
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

    def setup_CV(
        self,
        startVoltage: float = 0,
        firstVoltageLimit: float = 0.6,
        secondVoltageLimit: float = 0,
        endVoltage: float = 0,
        scanRate: float = 0.1,
        samplingInterval: float = 0.01,
        cycles=1,
    ):
        """Perform a cyclic voltammetry experiment on the potentiostat

        Args:
            startVoltage (float): The start potential of the cyclic
                voltammetry experiment
            firstVoltageLimit (float): The first voltage limit of the cyclic
                voltammetry experiment
            secondVoltageLimit (float): The second voltage limit of the cyclic
                voltammetry experiment
            endVoltage (float): The end voltage of the cyclic voltammetry
                experiment
            scanRate (float): The scan rate of the cyclic voltammetry
                experiment in V/s
            samplingInterval (float): The sampling interval in seconds
            cycles (int): The number of cycles to perform
        """

        print("\n*** Preparing CV experiment")
        experiment = AisExperiment()
        element = AisCyclicVoltammetryElement(
            startVoltage,
            firstVoltageLimit,
            secondVoltageLimit,
            endVoltage,
            scanRate,
            samplingInterval,
        )
        experiment.appendElement(element, cycles)
        self.upload_experiment(experiment)
        self.start_experiment()

    def run_experiment(self):
        """Run an experiment on the potentiostat. Remember to define the experiment first,
        for instance using setup_potentiostaticEIS() or setup_CV().

        """
        self.app.exec_()

    def close_experiment(self):
        """Close the experiment on the potentiostat and release the Qt application.
        Remember to call get_data() before calling this function to retrieve the data.

        """
        self.__del__()


measurement = AdmiralWrapper(port="COM5")

measurement.setup_potentiostaticEIS()
measurement.run_experiment()
ac_data_eis, dc_data_eis = measurement.get_data()
measurement.clear_data()
measurement.setup_CV(startVoltage=0, firstVoltageLimit=0.3, secondVoltageLimit=0, endVoltage=0, scanRate=0.1, samplingInterval=0.1, cycles=1)
measurement.run_experiment()
ac_data_cv, dc_data_cv = measurement.get_data()
measurement.close_experiment()

print("EIS data:")
print(ac_data_eis)
print(dc_data_eis)
print("CV data:")
print(ac_data_cv)
print(dc_data_cv)
