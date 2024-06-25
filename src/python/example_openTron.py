import logging
from datetime import datetime
import time
import sys
import json
import os
from opentronsHTTPAPI_clientBuilder import opentronsClient
from parameters import (
    labware_paths,
    wells,
    pipetteable_chemicals,
    labware_tools,
    pipette_tips,
    tool_x_offset,
    tool_y_offset,
    tool_z_offset,
    tool_z_dropoff,
    pipetteable_chemical_racks,
)

OPENTRON_IP = "100.67.86.197"
DATA_PATH = os.getcwd()
OPENTRON_PIPETTE = "p1000_single_gen2"
path = os.path.join(DATA_PATH, "src", "opentron_labware", "nis_4_tiprack_1ul.json")
print(path)
chemicals_to_mix = {
    "NH4OH": 1200,
    "KCHO": 1000,
    "Ni": 1000,
    "Fe": 1000,
    "Cr": 1000,
    "Mn": 1000,
    "Co": 1000,
    "Zn": 1000,
    "Cu": 1000,
}

# Initialize logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("example_opentron.log", mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
time_now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")


# Read JSON
def read_json(path: str) -> dict:
    with open(path, encoding="utf8") as f:
        return json.load(f)


# Initiate the openTron
openTron = opentronsClient(OPENTRON_IP)


##### Load labware for the openTron
# add pipette
openTron.loadPipette(strPipetteName=OPENTRON_PIPETTE, strMount="right")

# Tools
path = os.path.join(DATA_PATH, labware_paths["nistall_4_tiprack_1ul"])
labware_tool_rack = read_json(path)
labware_tool_rack = openTron.loadCustomLabware(
    dicLabware=labware_tool_rack,
    intSlot=10,
)
openTron.addLabwareOffsets(
    strLabwareName=labware_tool_rack,
    fltXOffset=0.7,
    fltYOffset=0.5,
    fltZOffset=5.2,
)

# Vials with solutions
path = os.path.join(DATA_PATH, labware_paths["nis_8_reservoir_25000ul"])
labware_stock_solutions1 = read_json(path)
labware_stock_solutions1 = openTron.loadCustomLabware(
    dicLabware=labware_stock_solutions1,
    intSlot=11,  # Remember to change in the parameters.py if slot is changed
)

# Vials with solutions
path = os.path.join(DATA_PATH, labware_paths["nis_8_reservoir_25000ul"])
labware_stock_solutions2 = read_json(path)
labware_stock_solutions2 = openTron.loadCustomLabware(
    dicLabware=labware_stock_solutions2,
    intSlot=7,  # Remember to change in the parameters.py if slot is changed
)

# Well plate where the testing takes place
path = os.path.join(DATA_PATH, labware_paths["nis_15_wellplate_3895ul"])
labware_well_plate = read_json(path)
labware_well_plate = openTron.loadCustomLabware(
    dicLabware=labware_well_plate, intSlot=9
)

# Cleaning cell for the openTron tools
path = os.path.join(DATA_PATH, labware_paths["nis_2_wellplate_30000ul"])
labware_cleaning_cartridge = read_json(path)
labware_cleaning_cartridge = openTron.loadCustomLabware(
    dicLabware=labware_cleaning_cartridge, intSlot=3
)
# Load pipette tip rack
labware_pipette_tips = openTron.loadLabware(
    intSlot=1, strLabwareName="opentrons_96_tiprack_1000ul"
)
openTron.addLabwareOffsets(
    strLabwareName=labware_pipette_tips, fltXOffset=0.5, fltYOffset=0.9, fltZOffset=-0.1
)

###############################################################################
# Workflow
###############################################################################
# Home robot
openTron.lights(True)
openTron.homeRobot()

# # To avoid cable clutter, move openTron first to pipette tip rack
# openTron.moveToWell(
#     strLabwareName=labware_pipette_tips,
#     strWellName=pipette_tips["NH4OH"],
#     strPipetteName=OPENTRON_PIPETTE,
#     strOffsetStart="top",
#     intOffsetX=0,
#     intOffsetY=0,
#     intOffsetZ=130,
#     intSpeed=100,  # mm/s
# )
# # Go to flush tool rack
# openTron.moveToWell(
#     strLabwareName=labware_tool_rack,
#     strWellName=labware_tools["Flush_tool"],
#     strPipetteName=OPENTRON_PIPETTE,
#     strOffsetStart="top",
#     intOffsetX=tool_x_offset["Flush_tool"],
#     intOffsetY=tool_y_offset["Flush_tool"],
#     intOffsetZ=50,
#     intSpeed=50,  # mm/s
# )
# # Pick up flush tool
# openTron.pickUpTip(
#     strLabwareName=labware_tool_rack,
#     strWellName=labware_tools["Flush_tool"],
#     strPipetteName=OPENTRON_PIPETTE,
#     strOffsetStart="top",
#     strOffsetX=tool_x_offset["Flush_tool"],
#     strOffsetY=tool_y_offset["Flush_tool"],
#     strOffsetZ=tool_z_offset["Flush_tool"],
# )

# # Go to well
# openTron.moveToWell(
#     strLabwareName=labware_well_plate,
#     strWellName=wells[0],
#     strPipetteName=OPENTRON_PIPETTE,
#     strOffsetStart="top",
#     intOffsetX=0,
#     intOffsetY=0,
#     intOffsetZ=-54,
#     intSpeed=50,  # mm/s
# )

# time.sleep(5)
# # Flush well with water
# # Drain well
# # Flush well with HCl
# # Apply ultrasound for 30 seconds
# # Drain well
# # Flush well with water
# # Drain well
# # Flush well with water
# # Drain well

# # Go to tool rack
# openTron.moveToWell(
#     strLabwareName=labware_tool_rack,
#     strWellName=labware_tools["Flush_tool"],
#     strPipetteName=OPENTRON_PIPETTE,
#     strOffsetStart="top",
#     intOffsetX=tool_x_offset["Flush_tool"],
#     intOffsetY=tool_y_offset["Flush_tool"],
#     intOffsetZ=50,
#     intSpeed=50,  # mm/s
# )
# # Drop tip
# openTron.dropTip(
#     strLabwareName=labware_tool_rack,
#     strWellName=labware_tools["Flush_tool"],
#     strPipetteName=OPENTRON_PIPETTE,
#     strOffsetStart="bottom",
#     strOffsetX=tool_x_offset["Flush_tool"],
#     strOffsetY=tool_y_offset["Flush_tool"],
#     strOffsetZ=tool_z_dropoff["Flush_tool"],
#     boolHomeAfter=False,
#     boolAlternateDropLocation=False,
# )


# # Go stright up in the air
# openTron.moveToWell(
#     strLabwareName=labware_tool_rack,
#     strWellName=labware_tools["Flush_tool"],
#     strPipetteName=OPENTRON_PIPETTE,
#     strOffsetStart="top",
#     intOffsetX=tool_x_offset["Flush_tool"],
#     intOffsetY=tool_y_offset["Flush_tool"],
#     intOffsetZ=100,
#     intSpeed=50,  # mm/s
# )


# # Loop through all chemicals to mix
# for chemical, volume in chemicals_to_mix.items():
#     logging.info(f"Mixing {chemical} with {volume} uL to well {wells[0]}")
#     # Move to pipette rack
#     openTron.moveToWell(
#         strLabwareName=labware_pipette_tips,
#         strWellName=pipette_tips[chemical],
#         strPipetteName=OPENTRON_PIPETTE,
#         strOffsetStart="top",
#         intOffsetX=0,
#         intOffsetY=0,
#         intOffsetZ=50,
#     )
#     # Pick up tip
#     openTron.pickUpTip(
#         strLabwareName=labware_pipette_tips,
#         strWellName=pipette_tips[chemical],
#         strPipetteName=OPENTRON_PIPETTE,
#         strOffsetStart="top",
#         strOffsetX=0,
#         strOffsetY=0,
#         strOffsetZ=0,
#     )

#     volume_left = volume
#     for dispense in range(0, volume, 1000):
#         if volume_left < 1000:
#             dispense_volume = volume_left
#         else:
#             dispense_volume = 1000

#         logging.info(f"Aspirating {dispense_volume} uL of {chemical}")
#         # Move to stock solution
#         openTron.moveToWell(
#             strLabwareName=pipetteable_chemical_racks[chemical],
#             strWellName=pipetteable_chemicals[chemical],
#             strPipetteName=OPENTRON_PIPETTE,
#             strOffsetStart="top",
#             intOffsetX=0,
#             intOffsetY=0,
#             intOffsetZ=0,
#         )
#         # Aspirate
#         openTron.aspirate(
#             strLabwareName=pipetteable_chemical_racks[chemical],
#             strWellName=pipetteable_chemicals[chemical],
#             strPipetteName=OPENTRON_PIPETTE,
#             intVolume=dispense_volume,  # uL
#             strOffsetStart="top",
#             strOffsetX=0,
#             strOffsetY=0,
#             strOffsetZ=-50,
#         )
#         # Go straight up in the air
#         openTron.moveToWell(
#             strLabwareName=pipetteable_chemical_racks[chemical],
#             strWellName=pipetteable_chemicals[chemical],
#             strPipetteName=OPENTRON_PIPETTE,
#             strOffsetStart="top",
#             intOffsetX=0,
#             intOffsetY=0,
#             intOffsetZ=80,
#         )
#         # Go to well
#         openTron.moveToWell(
#             strLabwareName=labware_well_plate,
#             strWellName=wells[0],
#             strPipetteName=OPENTRON_PIPETTE,
#             strOffsetStart="top",
#             intOffsetX=0,
#             intOffsetY=0,
#             intOffsetZ=10,
#         )
#         logging.info(f"Dispensing {dispense} uL of {chemical}")
#         # Dispense
#         openTron.dispense(
#             strLabwareName=labware_well_plate,
#             strWellName=wells[0],
#             strPipetteName=OPENTRON_PIPETTE,
#             intVolume=dispense_volume,  # uL
#             strOffsetStart="top",
#             strOffsetX=0,
#             strOffsetY=0,
#             strOffsetZ=0,
#         )
#         volume_left -= dispense_volume

#     # Go to pipette tip rack
#     openTron.moveToWell(
#         strLabwareName=labware_pipette_tips,
#         strWellName=pipette_tips[chemical],
#         strPipetteName=OPENTRON_PIPETTE,
#         strOffsetStart="top",
#         intOffsetX=0,
#         intOffsetY=0,
#         intOffsetZ=20,
#     )
#     logging.info(f"Dropping tip for {chemical}")
#     # Drop tip
#     openTron.dropTip(
#         strLabwareName=labware_pipette_tips,
#         strWellName=pipette_tips[chemical],
#         strPipetteName=OPENTRON_PIPETTE,
#         strOffsetStart="bottom",
#         strOffsetX=0,
#         strOffsetY=0,
#         strOffsetZ=10,
#         boolHomeAfter=False,
#         boolAlternateDropLocation=False,
#     )


# Go to Ni deposition tool
openTron.moveToWell(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Ni_electrode"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=50,
)
# Pick up Ni deposition tool
openTron.pickUpTip(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Ni_electrode"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    strOffsetX=tool_x_offset["Ni_electrode"],
    strOffsetY=tool_y_offset["Ni_electrode"],
    strOffsetZ=tool_z_offset["Ni_electrode"],
)
# # Go straight up in the air
# openTron.moveToWell(
#     strLabwareName=labware_tool_rack,
#     strWellName=labware_tools["Ni_electrode"],
#     strPipetteName=OPENTRON_PIPETTE,
#     strOffsetStart="top",
#     intOffsetX=tool_x_offset["Ni_electrode"],
#     intOffsetY=tool_y_offset["Ni_electrode"],
#     intOffsetZ=100,
# )
# Go to well at slow speed due to cable clutter
openTron.moveToWell(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=0,
    intSpeed=50,  # mm/s
)
# Go down in the well
openTron.moveToWell(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=-15,
    intSpeed=50,  # mm/s
)
time.sleep(5)
# Go straight up from the well
openTron.moveToWell(
    strLabwareName=labware_well_plate,
    strWellName=wells[0],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=0,
    intOffsetY=0,
    intOffsetZ=20,
    intSpeed=50,  # mm/s
)
# Go to tool rack Ni deposition tool
openTron.moveToWell(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Ni_electrode"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="top",
    intOffsetX=tool_x_offset["Ni_electrode"],
    intOffsetY=tool_y_offset["Ni_electrode"],
    intOffsetZ=20,
    intSpeed=50,  # mm/s
)
# Drop Ni deposition tool
openTron.dropTip(
    strLabwareName=labware_tool_rack,
    strWellName=labware_tools["Ni_electrode"],
    strPipetteName=OPENTRON_PIPETTE,
    strOffsetStart="bottom",
    strOffsetX=tool_x_offset["Ni_electrode"],
    strOffsetY=tool_y_offset["Ni_electrode"],
    strOffsetZ=tool_z_dropoff["Ni_electrode"],
    boolHomeAfter=False,
    boolAlternateDropLocation=False,
)

openTron.lights(False)
exit()

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
