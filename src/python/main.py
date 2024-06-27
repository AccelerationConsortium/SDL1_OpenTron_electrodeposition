import logging
from datetime import datetime
import sys
from experiment import Experiment

# Folder where data and log-file will be saved
DATA_PATH = ""
NAME_OF_ARDUINO = "CH340"  # Arduino name on Windows for auto finding COM port
chemicals_to_mix = {
    "NH4OH": 0,
    "KCHO": 0,
    "Ni": 1,
    "Fe": 0,
    "Cr": 0,
    "Mn": 0,
    "Co": 0,
    "Zn": 0,
    "Cu": 0,
}


# Initialize logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(DATA_PATH + "main.log", mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
time_now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

experiment = Experiment(
    well_volume=2.5,
    cleaning_station_volume=15,
    openTron_IP="100.67.86.197",
    arduino_usb_name="CH340",
)

experiment.run_experiment(chemicals_to_mix=chemicals_to_mix, dispense_ml_electrolyte=3, well_number = 0)

# Return potential at 10 mA/cm^2s
print("Done\n")
