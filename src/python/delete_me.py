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
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(DATA_PATH + "delete_me.log", mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
time_now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

experiment = Experiment(
    well_volume=2.5,
    cleaning_station_volume=4,
    openTron_IP="100.67.86.197",
    arduino_usb_name="CH340",
)
# Flush the electrode in the cleaning station/cartridge

# Prime pumps for flush tool
experiment.arduino.dispense_ml(pump=1, volume=1)
experiment.arduino.dispense_ml(pump=2, volume=1)

# Prime pumps for cleaning cartridge
# experiment.arduino.dispense_ml(pump=3, volume=5)
# experiment.arduino.dispense_ml(pump=4, volume=5)
# experiment.arduino.dispense_ml(pump=3, volume=5)
# experiment.arduino.dispense_ml(pump=5, volume=5)
# experiment.arduino.dispense_ml(pump=3, volume=5)


# Return potential at 10 mA/cm^2s
print("Done\n")
