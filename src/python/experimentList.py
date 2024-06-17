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

# function to return constantCurrent element
def setConstantCurrent(holdAtCurrent, samplingInterval, duration):
    constantCurrent = AisConstantCurrentElement(holdAtCurrent, samplingInterval, duration)
    return constantCurrent

# function to return constantPotential element
def setConstantPotential(holdAtVoltage, samplingInterval, duration):
    constantPotential = AisConstantPotElement(holdAtVoltage, samplingInterval, duration)
    return constantPotential

# function to return constantPower element
def setConstantPower(isCharge, powerVal, duration, samplingInterval):
    constantPower = AisConstantPowerElement(isCharge, powerVal, duration, samplingInterval)
    return constantPower

# function to return constantResistance element
def setConstantResistance(resistanceVal, duration, samplingInterval):
    constantResistance = AisConstantResistanceElement(resistanceVal, duration, samplingInterval)
    return constantResistance


# function to return CV element
def setCyclicVoltammetry(startPotential, firstVoltageLimit, secondVoltageLimit, endVoltage, scanRate, samplingInterval):
    cyclicVoltammetry = AisCyclicVoltammetryElement(startPotential, firstVoltageLimit, secondVoltageLimit, endVoltage, scanRate, samplingInterval)
    return cyclicVoltammetry

# function to return dcCurrentSweep element
def setDCCurrentSweep(startCurrent, endCurrent, scanRate, samplingInterval):
    dcCurrentSweep = AisDCCurrentSweepElement(startCurrent, endCurrent, scanRate, samplingInterval)
    return dcCurrentSweep

# function to return dcPotentialSweep element
def setDCPotentialSweep(startPotential, endPotential, scanRate, samplingInterval):
    dcPotentialSweep = AisDCPotentialSweepElement(startPotential, endPotential, scanRate, samplingInterval)
    return dcPotentialSweep

# function to return diffPulse element
def setDiffPulse(startPotential, endPotential, potentialStep, pulseHeight, pulseWidth, pulsePeriod):
    diffPulse = AisDiffPulseVoltammetryElement(startPotential, endPotential, potentialStep, pulseHeight, pulseWidth, pulsePeriod)
    return diffPulse

# function to return normalPulse element
def setNormalPulse(startPotential, endPotential, potentialStep, pulseWidth, pulsePeriod):
    normalPulse = AisNormalPulseVoltammetryElement(startPotential, endPotential, potentialStep, pulseWidth, pulsePeriod)
    return normalPulse

# function to return squareWave element
def setSquareWave(startPotential, endPotential, potentialStep, pulseAmp, pulseFrequency):
    squareWave = AisSquareWaveVoltammetryElement(startPotential, endPotential, potentialStep, pulseAmp, pulseFrequency)
    return squareWave

# function to return eisGalvanostatic element
def setEISGalvanostatic(startFrequency, endFrequency, stepsPerDecade, currentBias, currentAmplitude):
    eisGalvanostatic = AisEISGalvanostaticElement(startFrequency, endFrequency, stepsPerDecade, currentBias, currentAmplitude)
    return eisGalvanostatic 

# function to return eisPotentiostatic element
def setEISPotentiostatic(startFrequency, endFrequency, stepsPerDecade, voltageBias, voltageAmplitude):
    eisPotentiostatic = AisEISPotentiostaticElement(startFrequency, endFrequency, stepsPerDecade, voltageBias, voltageAmplitude)
    return eisPotentiostatic

# function to return openCircuit element
def setOpenCircuit(duration, samplingInterval):
    openCircuit = AisOpenCircuitElement(duration, samplingInterval)
    return openCircuit