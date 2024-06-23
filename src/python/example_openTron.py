import logging
from datetime import datetime
import sys
import json
from opentronwrapper import opentronsClient
from parameters import (
    labware_paths,
    wells,
    pipetteable_chemicals,
    labware_tools,
    pipette_tips,
)

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


# Read JSON
def read_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


##### Load labware for the openTron
# Tools
labware_tool_rack = read_json(labware_paths["nis_4_tip_rack_1ul"])
labware_tool_rack = openTron.loadCustomLabware(dicLabware=labware_tool_rack, inSlot=10)

# Vials with solutions
labware_stock_solutions1 = read_json(labware_paths["nis_8_reservoir_25000ul"])
labware_stock_solutions1 = openTron.loadCustomLabware(
    dicLabware=labware_stock_solutions1, inSlot=4
)
# Vials with solutions
labware_stock_solutions2 = read_json(labware_paths["nis_8_reservoir_25000ul"])
labware_stock_solutions2 = openTron.loadCustomLabware(
    dicLabware=labware_stock_solutions2, inSlot=5
)
# Well plate where the testing takes place
labware_well_plate = read_json(labware_paths["nis_15_wellplate_3895ul"])
labware_well_plate = openTron.loadCustomLabware(dicLabware=labware_well_plate, inSlot=6)
# Cleaning cell for the openTron tools
labware_cleaning_cartridge = read_json(labware_paths["nis_2_wellplate_30000ul"])
labware_cleaning_cartridge = openTron.loadCustomLabware(
    dicLabware=labware_cleaning_cartridge, inSlot=7
)
# Load pipette tip rack
labware_pipette_tips = openTron.loadLabware(1, "opentrons_96_tiprack_1000ul")

###############################################################################
# Workflow
###############################################################################
# Home robot
openTron.homeRobot()

# Go to flush tool rack
openTron.moveToWell(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Pick up flush tool
openTron.pickUpTip(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
)

# Go to well
openTron.moveToWell(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
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

# Go to tool rack
openTron.moveToWell(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Drop tip
openTron.dropTip(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="bottom",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=5,
    boolHomeAfter=False,
    boolAlternateDropLocation=False,
)

# Move to pipette rack
openTron.moveToWell(
    strLabwareName=labware_pipette_tips,
    strWellName=pipette_tips["NH4OH"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Pick up tip
openTron.pickUpTip(
    strLabwareName=labware_pipette_tips,
    strWellName=pipette_tips["NH4OH"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
)
# Move to stock solution
openTron.moveToWell(
    strLabwareName=labware_stock_solutions1,
    strWellName=pipetteable_chemicals["NH4OH"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Aspirate
openTron.aspirate(
    strLabwareName=labware_stock_solutions1,
    strWellName=pipetteable_chemicals["NH4OH"],
    strPipetteName=OPENTRON_PIPETTE,
    intVolume=1000,  # uL
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
)
# Go to well
openTron.moveToWell(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Dispense
openTron.dispense(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    intVolume=1000,  # uL
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
)

# Go to pipette tip rack
openTron.moveToWell(
    strLabwareName=labware_pipette_tips,
    strWellName=pipette_tips["NH4OH"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)

# Drop tip
openTron.dropTip(
    strLabwareName=labware_pipette_tips,
    strWellName=pipette_tips["NH4OH"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="bottom",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=5,
    boolHomeAfter=False,
    boolAlternateDropLocation=False,
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

# Go to tool rack flush tool
openTron.moveToWell(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Pick up flush tool
openTron.pickUpTip(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
)
# Go to well
openTron.moveToWell(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
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
openTron.moveToWell(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Drop tip
openTron.dropTip(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="bottom",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=5,
    boolHomeAfter=False,
    boolAlternateDropLocation=False,
)

# Pipette 80% of the volume of KOH into the well
openTron.moveToWell(
    strLabwareName=labware_pipette_tips,
    strWellName=pipette_tips["KOH"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Pick up tip
openTron.pickUpTip(
    strLabwareName=labware_pipette_tips,
    strWellName=pipette_tips["KOH"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
)
# Move to stock solution
openTron.moveToWell(
    strLabwareName=labware_stock_solutions1,
    strWellName=pipetteable_chemicals["KOH"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Aspirate
openTron.aspirate(
    strLabwareName=labware_stock_solutions1,
    strWellName=pipetteable_chemicals["KOH"],
    strPipetteName=OPENTRON_PIPETTE,
    intVolume=1000,  # uL
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
)
# Go to well
openTron.moveToWell(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Dispense
openTron.dispense(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    intVolume=1000,  # uL
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
)

# Go to pipette tip rack
openTron.moveToWell(
    strLabwareName=labware_pipette_tips,
    strWellName=pipette_tips["KOH"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Drop tip
openTron.dropTip(
    strLabwareName=labware_pipette_tips,
    strWellName=pipette_tips["KOH"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="bottom",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=5,
    boolHomeAfter=False,
    boolAlternateDropLocation=False,
)

# Go to tool rack OER_electrode
openTron.moveToWell(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["OER_electrode"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Pick up OER electrode
openTron.pickUpTip(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["OER_electrode"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
)
# Go to well
openTron.moveToWell(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)

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

# Clean OER electrode in cleaning cartridge
# Go to cleaning cartridge
openTron.moveToWell(
    strLabwareName=labware_cleaning_cartridge,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Hold it a bit
time.sleep(5)
# Go to rack tool to replace OER electrode
openTron.moveToWell(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["OER_electrode"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Drop OER electrode
openTron.dropTip(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["OER_electrode"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="bottom",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=5,
    boolHomeAfter=False,
    boolAlternateDropLocation=False,
)

# Go to flush tool
openTron.moveToWell(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Pick up flush tool
openTron.pickUpTip(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    strOffsetX=0,
    strOffsetY=0,
    strOffsetZ=0,
)
# Go to well
openTron.moveToWell(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Flush well with water
# Apply ultrasound
# Drain well
# Stop ultrasound
# Flush well with water
# Apply ultrasound
# Drain well
# Stop ultrasound

# Put back the flush tool
openTron.moveToWell(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
)
# Drop tip
openTron.dropTip(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Flush_tool"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="bottom",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=5,
    boolHomeAfter=False,
    boolAlternateDropLocation=False,
)

# Return potential at 10 mA/cm^2s
