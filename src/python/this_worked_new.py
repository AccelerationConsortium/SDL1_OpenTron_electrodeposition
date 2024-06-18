from PySide2.QtWidgets import QApplication
from SquidstatPyLibrary import (
    AisDeviceTracker,
    AisExperiment,
    AisEISPotentiostaticElement,
)
import sys


class EISMeasurement:
    def __init__(self):
        self.app = QApplication()
        self.tracker = AisDeviceTracker.Instance()
        self.handler = None

        self.dc_data_list = []
        self.ac_data_list = []
        self.new_element_list = []

    def handle_dc_data(self, channel, data):
        self.dc_data_list.append((data.timestamp, data.workingElectrodeVoltage))

    def handle_ac_data(self, channel, data):
        self.ac_data_list.append(
            (data.frequency, data.absoluteImpedance, data.phaseAngle)
        )

    def handle_new_element(self, channel, data):
        self.new_element_list.append(
            (data.stepName, data.stepNumber, data.substepNumber)
        )

    def on_device_connected(self, device_name):
        print("Device is Connected: %s" % device_name)

    # def handle_dc_data(self, channel, data):
    #     print(
    #         "timestamp:",
    #         "{:.9f}".format(data.timestamp),
    #         "workingElectrodeVoltage: ",
    #         "{:.9f}".format(data.workingElectrodeVoltage),
    #     )

    # def handle_ac_data(self, channel, data):
    #     print(
    #         "frequency:",
    #         "{:.9f}".format(data.frequency),
    #         "absoluteImpedance: ",
    #         "{:.9f}".format(data.absoluteImpedance),
    #         "phaseAngle: ",
    #         "{:.9f}".format(data.phaseAngle),
    #     )

    # def handle_new_element(self, channel, data):
    #     print(
    #         "New experiment/node beginning:",
    #         data.stepName,
    #         "step number: ",
    #         data.stepNumber,
    #         " step sub : ",
    #         data.substepNumber,
    #     )

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

    def run_experiment(self):
        experiment = AisExperiment()
        eis_element = AisEISPotentiostaticElement(10000, 1000, 10, 0.0, 0.1)
        experiment.appendElement(eis_element, 1)

        error = self.handler.uploadExperimentToChannel(0, experiment)
        if error != 0:
            print(error.message())

        error = self.handler.startUploadedExperiment(0)
        if error != 0:
            print(error.message())

        # self.app.exec_()  # Execute the code above, in particular the signal handlers
        sys.exit(self.app.exec_())


eis_measurement = EISMeasurement()
eis_measurement.connect_to_device("COM5")
eis_measurement.setup_data_handlers()
eis_measurement.run_experiment()
print("DC Data:")
print(eis_measurement.dc_data_list)
print("AC Data:")
print(eis_measurement.ac_data_list)
