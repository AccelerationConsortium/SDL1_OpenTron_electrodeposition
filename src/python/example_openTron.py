import logging
from datetime import datetime
import sys
from opentronwrapper import opentronsClient

# Folder where data and log-file will be saved
DATA_PATH = ""
OPENTRON_PIPETTE = "p1000_single_gen2"


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
openTron = opentronsClient("100.67.86.197")

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
# Put back the Ni deposition tool

# # Pick up the flush tool
# # Go to well
# # Flush well with water
# # Apply ultrasound
# # Drain well
# # Stop ultrasound
# # Flush well with HCl
# # Apply ultrasound
# # Drain well
# # Flush well with water
# # Drain well
# # Flush well with water
# # Drain well
# # Stop ultrasound

# # Put back the flush tool

# # Pipette 80% of the volume of KOH into the well

# # Pick up electrochemical testing electrode

# Electrochemical testing
# 0 - Electrochemical Activation

# 1 - Perform CV
# 2 - Perform CV

# 3 - Perform EIS

# 4 - Perform CP at 100 mA/cm^2
# 5 - Perform CP at 50 mA/cm^2
# 6 - Perform CP at 20 mA/cm^2
# 7 - Perform CP at 10 mA/cm^2
# 8 - Perform CP at 5 mA/cm^2
# 9 - Perform CP at 2 mA/cm^2
# 10 - Perform CP at 1 mA/cm^2
# 11 - Perform CV


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
