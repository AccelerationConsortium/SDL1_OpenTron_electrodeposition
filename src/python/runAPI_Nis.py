import SquidstatPyLibrary as SquidLib
import os
import sys
import ExperimentList as AiAPIExperimentList

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

data_collector = DataCollector()

class FileWriter:
    def __init__(self, filename):
        output_dir = "Output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)  # Create the directory if it doesn't exist

        # Adjust the file path to include the output directory
        filepath = os.path.join(output_dir, filename)
        self.file = open(filepath, 'w')  # Open file for writing in the output directory

    def write(self, line):
        self.file.write(line + '\n')  # Write line to file with newline character

    def close(self):
        self.file.close()  # Close the file

# Create an instance of the FileWriter class
# get file name from user input when starting script
file_writer = FileWriter(sys.argv[1])
# set up headers
file_writer.write(str("Timestamp, WorkingElectrodePotential, WorkingElectrodeCurrent, Temperature"))

# TODO put somewhere else!
# tell me it is starting
# print("starting cyclic voltammetry experiment via API")

# define application
app = QApplication()
# device tracker
tracker = AisDeviceTracker.Instance()
# find device and report name
tracker.newDeviceConnected.connect(lambda deviceName: print("Device is Connected: %s" % deviceName))

# instantiate experiment
experiment = AisExperiment()
subExperiment = AisExperiment()
subExperiment2 = AisExperiment()


tracker.connectToDeviceOnComPort("COM15")
handler = tracker.getInstrumentHandler("Cycler1409")

# quit app needed to write to file via pipe
def quitapp(channel):
    print("Experiment Completed: %d" % channel)
    app.quit()


def skipExperiment(channel, data):
    global steps
    print(f"step is now at {steps}")
    # OCP will be step 1
    # should hold here until for 600 seconds since duration = 600
    if steps == 1:
        if data.temperature > 30:
            # should skip to dcCurrentSweep, then hold at step 3 which is OCP for 600 seconds
            handler.skipExperimentStep(0)
    # holds at 2nd OCP while the temperature drops
    if steps == 3:
        if data.temperature < 30:
            # skips to constantCurrent
            handler.skipExperimentStep(0)
    # holds at 3rd OCP while the temperature rises
    if steps == 5:
        if data.temperature > 30:
            # skips to constantPotential
            handler.skipExperimentStep(0)

# function for printing a new node when it begins
def on_experiment_new_element_starting(channel, data:AisExperimentNode):
    global steps
    steps += 1
    print(f"Step = {steps}")
    #print(f"New Node beginning {data.stepName}, step number {data.stepNumber}, step sub: {data.substepNumber}")

# where data is actually handled, prints to console
handler.activeACDataReady.connect(lambda channel, data: print("timestamp: ,", "{:.9f}".format(data.timestamp), "frequency:", "{:.9f}".format(data.frequency), "absoluteImpedance: ", "{:.9f}".format(data.absoluteImpedance), "phaseAngle: ", "{:.9f}".format(data.phaseAngle)))
handler.activeDCDataReady.connect(lambda channel, data: print("timestamp: ,", "{:.9f}".format(data.timestamp), ", workingElectrodeVoltage: ,", "{:.9f}".format(data.workingElectrodeVoltage), ", workingElectrodeCurrent: ,", "{:.9f}".format(data.current), ", Temperature, ", "{:.2f}".format(data.temperature)))
handler.activeDCDataReady.connect(skipExperiment)
handler.experimentNewElementStarting.connect(lambda channel, data: print("New Node beginning:", data.stepName, "step number: ", data.stepNumber, " repeat number : ", data.substepNumber))
handler.experimentNewElementStarting.connect(on_experiment_new_element_starting)
# stop the experiment and give the terminal back
handler.experimentStopped.connect(quitapp)

# Write the data
def writeData(channel, data):
    data_collector.add_data(data.timestamp, data.workingElectrodeVoltage, data.current)
    file_writer.write(str(data.timestamp) + "," + str(data.workingElectrodeVoltage) + "," + str(data.current) + "," + str(data.temperature))


# write data when it comes in
handler.activeDCDataReady.connect(writeData)

# region
# Setup experiments
constantCurrent = AiAPIExperimentList.setConstantCurrent(holdAtCurrent, samplingInterval, duration)
constantPotential = AiAPIExperimentList.setConstantPotential(holdAtVoltage, samplingInterval, duration)
constantPower = AiAPIExperimentList.setConstantPower(isCharge, powerVal, duration, samplingInterval)
constantResistance = AiAPIExperimentList.setConstantResistance(resistanceVal, duration, samplingInterval)

dcCurrentSweep = AiAPIExperimentList.setDCCurrentSweep(startCurrent, endCurrent, scanRate, samplingInterval)

dcPotentialSweep = AiAPIExperimentList.setDCPotentialSweep(firstVoltageLimit, secondVoltageLimit, scanRate, samplingInterval)
cyclicVoltammetry = AiAPIExperimentList.setCyclicVoltammetry(startPotential, firstVoltageLimit, secondVoltageLimit, endVoltage, scanRate, samplingInterval)

diffPulse = AiAPIExperimentList.setDiffPulse(firstVoltageLimit, secondVoltageLimit, potentialStep, pulseHeight, pulseWidth, pulsePeriod)
normalPulse = AiAPIExperimentList.setNormalPulse(firstVoltageLimit, secondVoltageLimit, potentialStep, pulseWidth, pulsePeriod)
squareWave = AiAPIExperimentList.setSquareWave(firstVoltageLimit, secondVoltageLimit, potentialStep, pulseAmplitude, pulseFrequency)

eisGalvanostatic = AiAPIExperimentList.setEISGalvanostatic(startFrequency, endFrequency, stepsPerDecade, currentBias, currentAmplitude)
eisPotentiostatic = AiAPIExperimentList.setEISPotentiostatic(startFrequency, endFrequency, stepsPerDecade, voltageBias, voltageAmplitude)

openCircuit = AiAPIExperimentList.setOpenCircuit(duration, samplingInterval)
# endregion


# append element to experiment with 1 repeat
# open circuit is basically a pause step
experiment.appendElement(openCircuit, 1)
experiment.appendElement(dcCurrentSweep, 1)

# open circuit is basically a pause step
subExperiment.appendElement(openCircuit, 1)
subExperiment.appendElement(constantCurrent, 1)

# open circuit is basically a pause step
experiment.appendElement(constantPotential, 1)

# send experiment to queue
handler.uploadExperimentToChannel(channelInUse, experiment)
# start experiment
handler.startUploadedExperiment(channelInUse)

# run program, starts qt
sys.exit(app.exec_())
