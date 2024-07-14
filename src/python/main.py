import logging
from datetime import datetime
import sys
from experiment import Experiment
import time

# Folder where data and log-file will be saved
DATA_PATH = ""
NAME_OF_ARDUINO = "CH340"  # Arduino name on Windows for auto finding COM port
chemicals_to_mix = [
    {
        "Ni": 1,
        "Fe": 1,
        "Cr": 1,
        "Mn": 1,
        "Co": 1,
        "Zn": 1,
        "Cu": 1,
        "NH4OH": 1,
        "NaCi": 1,
    },
]


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


## Priming of pumps
# experiment = Experiment(
#     well_volume=2.5,
#     cleaning_station_volume=6,
#     openTron_IP="100.67.86.197",
#     arduino_usb_name="CH340",
# )
# experiment.arduino.set_temperature(1, 35)
# experiment.cleaning(3)
# experiment.cleaning(4)


logging.info("Sleep 600 seconds to heat up the well plate to 35C")
# time.sleep(600)
# experiment.arduino.dispense_ml(pump=1, volume=2)
# experiment.arduino.dispense_ml(pump=2, volume=2)
# experiment.arduino.dispense_ml(pump=3, volume=5)
# experiment.arduino.dispense_ml(pump=4, volume=4)
# experiment.arduino.dispense_ml(pump=3, volume=4)
# experiment.arduino.dispense_ml(pump=4, volume=4)
# experiment.arduino.dispense_ml(pump=3, volume=4)

# experiment.__del__()

tid = [2,10,30,60,90]
for i in range(0, 5):
    logging.info(f"\n\n\nStarting experiment {i}")
    experiment = Experiment(
        well_volume=2.5,
        cleaning_station_volume=6,
        openTron_IP="100.67.86.197",
        arduino_usb_name="CH340",
    )
    experiment.arduino.set_temperature(1, 35)
    corrected_potential_10mA = experiment.run_experiment(
        chemicals_to_mix=chemicals_to_mix[i],
        dispense_ml_electrolyte=3,
        electrodeposition_time=tid[i],
        electrodeposition_temperature=35,
        chemical_ultrasound_mixing_time=30,
        chemical_rest_time=300,
    )
    experiment.arduino.set_temperature(1, 0)
    experiment.__del__()
    logging.info(f"Done with experiment {i}\n\n\n")


# Return potential at 10 mA/cm^2s
print("Done with experiments\n")
