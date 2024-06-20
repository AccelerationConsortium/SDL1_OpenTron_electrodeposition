from ardu import Arduino
import logging
from datetime import datetime
import sys
from opentronsHTTPAPI_clientBuilder import opentronsClient

# Folder where data and log-file will be saved
DATA_PATH = ""
NAME_OF_ARDUINO = "CH340"
OPENTRON_PIPETTE = "p1000_single_gen2"

# Surface area of sample in cm^2
sample_surface_area = 0.2827
current_density = 0.020  # A/cm^2
current_at_sample = sample_surface_area * current_density
volume_of_well = 3.9  # mL
volume_of_pipette = 1  # mL

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(DATA_PATH + "main.log", mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
time_now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

# Initiate the openTron
openTron = opentronsClient("100.64.78.193")

##### Load labware for the openTron
# Tools
openTron.loadLabware(3, "../opentron_labware/nis_4_tip_rack_1ul.json")
OT_tool_rack = "nis_4_tip_rack_1ul"
# Vials with solutions
openTron.loadLabware(7, "../opentron_labware/nis_8_reservoir_25000ul.json")
# Vials with solutions
openTron.loadLabware(11, "../opentron_labware/nis_8_reservoir_25000ul.json")
# Well plate where the testing takes place
openTron.loadLabware(8, "../opentron_labware/nis_15_wellplate_3895ul.json")
OT_well_plate = "nis_15_wellplate_3895ul"
# Cleaning cell for the openTron tools
openTron.loadLabware(9, "../opentron_labware/nis_2_wellplate_30000ul.json")
# Load pipette tip rack
openTron.loadLabware(1, "../opentron_labware/opentrons_96_tiprack_1000ul.json")

###############################################################################
# Workflow
###############################################################################

# Pick up flush tool
openTron.moveToWell(
    strLabwareName=OT_tool_rack,
    strWellName="A1",
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
openTron.pickUpTip(
    strLabwareName=OT_tool_rack,
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
    strWellName="A1",
)

# Go to well
openTron.moveToWell(
    strLabwareName=OT_well_plate,
    strWellName="A1",
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)

# Flush well with water
# Drain well
# Flush well with HCl
# Apply ultrasound for 30 seconds
# Drain well
# Flush well with water
# Drain well
# Flush well with water
# Drain well

# Put back flush tool
openTron.moveToWell(
    strLabwareName=OT_well_plate,
    strWellName="A1",
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
openTron.dropTip(
    strPipetteName=OPENTRON_PIPETTE,
    strLabwareName=OT_tool_rack,
    strWellName="A1",
    strOffsetStart="center",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
    boolHomeAfter=False,
    boolAlternateDropLocation=False,
)

# Pipette NH4OH into well
openTron.pickUpTip(
    strLabwareName=OT_tool_rack,
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
    strWellName="A1",
)

# Pipette KCHO into well
# Pipette Ni into well
# Pipette Fe into well
# Pipette Cr into well
# Pipette Mn into well
# Pipette Co into well
# Pipette Zn into well
# Pipette Cu into well

# Pick up Ni deposition tool

# Go to well and park with the tip dipped in the well

# Apply constant current for X seconds
measurement.setup_constant_current(
    holdAtCurrent=current_at_sample, samplingInterval=0.1, duration=10
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# Put back the Ni deposition tool

# Pick up the flush tool
# Go to well
# Flush well with water
# Apply ultrasound
# Drain well
# Stop ultrasound
# Flush well with HCl
# Apply ultrasound
# Drain well
# Flush well with water
# Drain well
# Flush well with water
# Drain well
# Stop ultrasound

# Put back the flush tool

# Pipette 80% of the volume of KOH into the well

# Pick up electrochemical testing electrode

# Electrochemical testing
# 0 - Electrochemical Activation
measurement.setup_constant_current(
    holdAtCurrent=0.2 * sample_surface_area, samplingInterval=0.05, duration=60
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 1 - Perform CV
measurement.setup_cyclic_voltammetry(
    startVoltage=1.6,
    firstVoltageLimit=0.8,
    secondVoltageLimit=1.6,
    endVoltage=1.6,
    scanRate=0.2,
    samplingInterval=0.05,
    cycles=25,
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 2 - Perform CV
measurement.setup_cyclic_voltammetry(
    startVoltage=1.6,
    firstVoltageLimit=0.8,
    secondVoltageLimit=1.6,
    endVoltage=0.8,
    scanRate=0.01,
    samplingInterval=0.2,
    cycles=2,
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 3 - Perform EIS
measurement.setup_EIS_potentiostatic(
    start_frequency=500000,
    end_frequency=1,
    points_per_decade=10,
    voltage_bias=1.5,
    voltage_amplitude=0.01,
    number_of_runs=1,
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 4 - Perform CP at 100 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.1 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 5 - Perform CP at 50 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.05 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 6 - Perform CP at 20 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.02 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 7 - Perform CP at 10 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.01 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 8 - Perform CP at 5 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.005 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 9 - Perform CP at 2 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.002 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 10 - Perform CP at 1 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.001 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 11 - Perform CV
measurement.setup_cyclic_voltammetry(
    startVoltage=1.6,
    firstVoltageLimit=0.8,
    secondVoltageLimit=1.6,
    endVoltage=0.8,
    scanRate=0.01,
    samplingInterval=0.2,
    cycles=2,
)


# Save all data
# Plot all data
# Find potential at 10 mA/cm^2

# Put back the electrochemical testing electrode

# Pick up the flush tool
# Go to well
# Flush well with water
# Apply ultrasound
# Drain well
# Stop ultrasound
# Flush well with water
# Apply ultrasound
# Drain well
# Stop ultrasound

# Put back the flush tool

# Return potential at 10 mA/cm^2s
