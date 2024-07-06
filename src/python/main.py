import logging
from datetime import datetime
import sys
from experiment import Experiment

# Folder where data and log-file will be saved
DATA_PATH = ""
NAME_OF_ARDUINO = "CH340"  # Arduino name on Windows for auto finding COM port
chemicals_to_mix = [
    {
        "Ni": 1,
        "Fe": 0,
        "Cr": 0,
        "Mn": 0,
        "Co": 0,
        "Zn": 0,
        "Cu": 0,
        "NH4OH": 0,
        "NaCi": 0,
    },
    {
        "Ni": 0,
        "Fe": 1,
        "Cr": 0,
        "Mn": 0,
        "Co": 0,
        "Zn": 0,
        "Cu": 0,
        "NH4OH": 0,
        "NaCi": 0,
    },
    {
        "Ni": 0,
        "Fe": 0,
        "Cr": 1,
        "Mn": 0,
        "Co": 0,
        "Zn": 0,
        "Cu": 0,
        "NH4OH": 0,
        "NaCi": 0,
    },
    {
        "Ni": 0,
        "Fe": 0,
        "Cr": 0,
        "Mn": 1,
        "Co": 0,
        "Zn": 0,
        "Cu": 0,
        "NH4OH": 0,
        "NaCi": 0,
    },
    {
        "Ni": 0,
        "Fe": 0,
        "Cr": 0,
        "Mn": 0,
        "Co": 1,
        "Zn": 0,
        "Cu": 0,
        "NH4OH": 0,
        "NaCi": 0,
    },
    {
        "Ni": 0,
        "Fe": 0,
        "Cr": 0,
        "Mn": 0,
        "Co": 0,
        "Zn": 1,
        "Cu": 0,
        "NH4OH": 0,
        "NaCi": 0,
    },
    {
        "Ni": 0,
        "Fe": 0,
        "Cr": 0,
        "Mn": 0,
        "Co": 0,
        "Zn": 0,
        "Cu": 1,
        "NH4OH": 0,
        "NaCi": 0,
    },
    {
        "Ni": 1,
        "Fe": 1,
        "Cr": 1,
        "Mn": 1,
        "Co": 1,
        "Zn": 1,
        "Cu": 1,
        "NH4OH": 0,
        "NaCi": 0,
    },
    {
        "Ni": 1,
        "Fe": 1,
        "Cr": 1,
        "Mn": 1,
        "Co": 1,
        "Zn": 1,
        "Cu": 1,
        "NH4OH": 1,
        "NaCi": 0,
    },
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
    {
        "Ni": 1,
        "Fe": 1,
        "Cr": 1,
        "Mn": 1,
        "Co": 1,
        "Zn": 1,
        "Cu": 1,
        "NH4OH": 0,
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


### Priming of pumps
experiment = Experiment(
    well_volume=2.5,
    cleaning_station_volume=6,
    openTron_IP="100.67.86.197",
    arduino_usb_name="CH340",
)
experiment.arduino.set_temperature(1, 35)
experiment.__del__()

# experiment.arduino.dispense_ml(pump=1, volume=2)
# experiment.arduino.dispense_ml(pump=2, volume=2)
# experiment.arduino.dispense_ml(pump=3, volume=5)
# experiment.arduino.dispense_ml(pump=4, volume=4)
# experiment.arduino.dispense_ml(pump=3, volume=4)
# experiment.arduino.dispense_ml(pump=4, volume=4)
# experiment.arduino.dispense_ml(pump=3, volume=4)

for i in range(0, 6):
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
        electrodeposition_time=60,
        electrodeposition_temperature=35,
        chemical_ultrasound_mixing_time=30,
        chemical_rest_time=300,
    )
    experiment.arduino.set_temperature(1, 0)
    experiment.__del__()
    logging.info(f"Done with experiment {i}\n\n\n")


# Return potential at 10 mA/cm^2s
print("Done with experiments\n")
