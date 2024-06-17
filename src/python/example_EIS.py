import sys
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


# function to return eisGalvanostatic element
def setEISGalvanostatic(startFrequency, endFrequency, stepsPerDecade, currentBias, currentAmplitude):
    eisGalvanostatic = AisEISGalvanostaticElement(startFrequency, endFrequency, stepsPerDecade, currentBias, currentAmplitude)
    return eisGalvanostatic 

# function to return eisPotentiostatic element
def setEISPotentiostatic(startFrequency, endFrequency, stepsPerDecade, voltageBias, voltageAmplitude):
    eisPotentiostatic = AisEISPotentiostaticElement(startFrequency, endFrequency, stepsPerDecade, voltageBias, voltageAmplitude)
    return eisPotentiostatic


import SquidstatPyLibrary as SquidLib
import os
import sys
from PySide2.QtWidgets import QApplication
from SquidstatPyLibrary import AisDeviceTracker
from SquidstatPyLibrary import AisCompRange
from SquidstatPyLibrary import AisDCData
from SquidstatPyLibrary import AisACData
from SquidstatPyLibrary import AisExperimentNode
from SquidstatPyLibrary import AisErrorCode
from SquidstatPyLibrary import AisExperiment
from SquidstatPyLibrary import AisInstrumentHandler


# region
steps = 0

# PARAMETERS
# A
holdAtCurrent = 0.4
startCurrent = 0.1
endCurrent = 0.6
currentBias = 0.0
currentAmplitude = 0.2

# bool
isCharge = False

# Hz
startFrequency = 10000.0
endFrequency = 10.0
pulseFrequency = 20
stepsPerDecade = 10

# ohm
resistanceVal = 100.0

# s
samplingInterval = 0.1
duration = 600
pulsePeriod = 0.2
pulseWidth = 0.02

# V
startPotential = 0.1
firstVoltageLimit = 0.6
secondVoltageLimit = 0.1
endVoltage = 0.01
holdAtVoltage = 0.5
potentialStep = 0.005
voltageBias = 0.0
voltageAmplitude = 0.2
pulseAmplitude = 0.01
pulseHeight = 0.01

# V/s
scanRate = 0.05

# W
powerVal = 0.0

# channelToUse
channelInUse = 0
# endregion

class DataCollector:
    def __init__(self):
        self.timestamps = []
        self.voltages = []
        self.currents = []

    def add_data(self, timestamp, voltage, current):
        self.timestamps.append(timestamp)
        self.voltages.append(voltage)
        self.currents.append(current)


# quit app needed to write to file via pipe
def quitapp(channel):
    print("Experiment Completed: %d" % channel)
    app.quit()


data_collector = DataCollector()

# define application
app = QApplication()
# device tracker
tracker = AisDeviceTracker.Instance()
# find device and report name
tracker.newDeviceConnected.connect(lambda deviceName: print("Device is Connected: %s" % deviceName))

# instantiate experiment
experiment = AisExperiment()

tracker.connectToDeviceOnComPort("COM5")
handler = tracker.getInstrumentHandler("Plus1894")

eisPotentiostatic = setEISPotentiostatic(
    startFrequency, endFrequency, stepsPerDecade, voltageBias, voltageAmplitude
)
experiment.appendElement(eisPotentiostatic, 1)
# send experiment to queue
handler.uploadExperimentToChannel(channelInUse, experiment)
# start experiment
handler.startUploadedExperiment(channelInUse)

# where data is actually handled, prints to console
handler.activeACDataReady.connect(lambda channel, data: print("timestamp: ,", "{:.9f}".format(data.timestamp), "frequency:", "{:.9f}".format(data.frequency), "absoluteImpedance: ", "{:.9f}".format(data.absoluteImpedance), "phaseAngle: ", "{:.9f}".format(data.phaseAngle)))
handler.activeDCDataReady.connect(lambda channel, data: print("timestamp: ,", "{:.9f}".format(data.timestamp), ", workingElectrodeVoltage: ,", "{:.9f}".format(data.workingElectrodeVoltage), ", workingElectrodeCurrent: ,", "{:.9f}".format(data.current), ", Temperature, ", "{:.2f}".format(data.temperature)))


# stop the experiment and give the terminal back
handler.experimentStopped.connect(quitapp)
