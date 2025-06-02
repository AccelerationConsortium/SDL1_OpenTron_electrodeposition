# IMPORT DEPENDENCIES------------------------------------------------------------------------------
import logging
from datetime import datetime
import sys
from experiment import Experiment

# -----INITIALIZE LOGGING-----
DATA_PATH = ""
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

#%%
# INITIALIZE EXPERIMENT----------------------------------------------------------------------------

chemicals_to_mix = [
    {
        "Ni": 0.10,
        "Fe": 0.10,
        "Cr": 0.10,
        "Mn": 0.10,
        "Co": 0.10,
        "Zn": 0.10,
        "Cu": 0.10,
        "NH4OH": 0.30,
        "NaCi": 0,
    },
]

experiment = Experiment(
    well_volume=2.5,
    cleaning_station_volume=6,
    openTron_IP="100.67.86.197",

)

experiment.openTron.lights(True)
experiment.openTron.homeRobot()

# clean well
experiment.cleaning(well_number = 0, sleep_time = 2)

# dispense metal-salt solutions
experiment.dose_chemicals(
    chemicals_to_mix = chemicals_to_mix[0],
    well_number = 0,
    total_volume = 2.5
)
# stir
experiment.arduino.set_ultrasound_on(1, 10)

# "electrodeposit"

experiment.perform_electrodeposition(
    well_number = 0,
    electrodeposition_time = 1
)

# clean well
experiment.cleaning(well_number = 0, sleep_time = 2)

# dispense electrolyte
experiment.dispense_electrolyte(
    volume = 3,
    chemical = "KOH",
    well_number = 0
)

# make sure relay is off
experiment.arduino.set_relay_off(8)


experiment.perform_electrochemical_testing(
    well_number = 0
)

experiment.cleaning(
    well_number = 0,
    sleep_time = 2
)
