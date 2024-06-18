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


def onDeviceConnected(deviceName):
    global DEVICE_NAME
    DEVICE_NAME = str(deviceName)
    print("Device is Connected: %s" % DEVICE_NAME)


def handleDCData(channel, data):
    print(
        "timestamp:",
        "{:.9f}".format(data.timestamp),
        "workingElectrodeVoltage: ",
        "{:.9f}".format(data.workingElectrodeVoltage),
    )


def handleACData(channel, data):
    print(
        "frequency:",
        "{:.9f}".format(data.frequency),
        "absoluteImpedance: ",
        "{:.9f}".format(data.absoluteImpedance),
        "phaseAngle: ",
        "{:.9f}".format(data.phaseAngle),
    )


def handleNewElement(channel, data):
    print(
        "New Node beginning:",
        data.stepName,
        "step number: ",
        data.stepNumber,
        " step sub : ",
        data.substepNumber,
    )


def handleExperimentStopped(channel):
    print("Experiment Completed: %d" % channel)


def connectToDevice(port, tracker):
    tracker.newDeviceConnected.connect(onDeviceConnected)
    tracker.connectToDeviceOnComPort(port)


def setupDataHandlers(handler):
    handler.activeDCDataReady.connect(handleDCData)
    handler.activeACDataReady.connect(handleACData)
    handler.experimentNewElementStarting.connect(handleNewElement)
    handler.experimentStopped.connect(handleExperimentStopped)


def runExperiment(port):
    app = QApplication()
    tracker = AisDeviceTracker.Instance()

    connectToDevice(port, tracker)
    handler = tracker.getInstrumentHandler("Plus1894")
    setupDataHandlers(handler)

    experiment = AisExperiment()
    eisElement = AisEISPotentiostaticElement(10000, 1000, 10, 0.0, 0.1)
    experiment.appendElement(eisElement, 1)

    error = handler.uploadExperimentToChannel(0, experiment)
    if error != 0:
        print(error.message())

    error = handler.startUploadedExperiment(0)
    if error != 0:
        print(error.message())

    app.quit()


DEVICE_NAME = ""
runExperiment("COM5")
