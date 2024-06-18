import sys
from PySide2.QtWidgets import QApplication
from typing import List
import SquidstatPyLibrary as SquidLib
from SquidstatPyLibrary import (
    AisDeviceTracker,
    AisCompRange,
    AisDCData,
    AisACData,
    AisExperimentNode,
    AisErrorCode,
    AisExperiment,
    AisInstrumentHandler,
    AisConstantPotElement,
    AisEISPotentiostaticElement,
    AisConstantCurrentElement,
    AisEISGalvanostaticElement,
)

AC_DATA_ARRAY: List[str] = []

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
    ac_data_str = (
        "frequency: {:.9f}, absoluteImpedance: {:.9f}, phaseAngle: {:.9f}".format(
            data.frequency, data.absoluteImpedance, data.phaseAngle
        )
    )
    AC_DATA_ARRAY.append(ac_data_str)


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
print(AC_DATA_ARRAY)
