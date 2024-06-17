import sys
import struct
from PySide2.QtWidgets import QApplication
import SquidstatPyLibrary as SquidLib
from SquidstatPyLibrary import AisDeviceTracker
from SquidstatPyLibrary import AisCompRange
from SquidstatPyLibrary import AisDCData
from SquidstatPyLibrary import AisACData
from SquidstatPyLibrary import AisExperimentNode
from SquidstatPyLibrary import AisErrorCode
from SquidstatPyLibrary import AisExperiment
from SquidstatPyLibrary import AisInstrumentHandler
from SquidstatPyLibrary import AisConstantPotElement
from SquidstatPyLibrary import AisEISPotentiostaticElement
from SquidstatPyLibrary import AisConstantCurrentElement
from SquidstatPyLibrary import AisEISGalvanostaticElement


def measure_EIS(port: str):
    app = QApplication()

    tracker = AisDeviceTracker.Instance()

    tracker.newDeviceConnected.connect(
        lambda deviceName: print("Device is Connected: %s" % deviceName)
    )
    tracker.connectToDeviceOnComPort(port)

    handler = tracker.getInstrumentHandler("Plus1894")

    handler.activeDCDataReady.connect(
        lambda channel, data: print(
            "timestamp:",
            "{:.9f}".format(data.timestamp),
            "workingElectrodeVoltage: ",
            "{:.9f}".format(data.workingElectrodeVoltage),
        )
    )
    handler.activeACDataReady.connect(
        lambda channel, data: print(
            "frequency:",
            "{:.9f}".format(data.frequency),
            "absoluteImpedance: ",
            "{:.9f}".format(data.absoluteImpedance),
            "phaseAngle: ",
            "{:.9f}".format(data.phaseAngle),
        )
    )
    handler.experimentNewElementStarting.connect(
        lambda channel, data: print(
            "New Node beginning:",
            data.stepName,
            "step number: ",
            data.stepNumber,
            " step sub : ",
            data.substepNumber,
        )
    )
    handler.experimentStopped.connect(
        lambda channel: print("Experiment Completed: %d" % channel)
    )

    experiment = AisExperiment()
    eisElement = AisEISPotentiostaticElement(10000, 1000, 10, 0.0, 0.1)
    experiment.appendElement(eisElement, 1)

    # upload experiment to channel 1
    error = handler.uploadExperimentToChannel(0, experiment)
    if error != 0:
        print(error.message())
        # return

    # start experiment on channel 1
    error = handler.startUploadedExperiment(0)
    if error != 0:
        print(error.message())

    app.quit()
    sys.exit(app.exec_())

    # Get the data from the potentiostat


measure_EIS("COM5")