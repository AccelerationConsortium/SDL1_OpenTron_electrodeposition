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
        "Ni": 0.10,
        "Fe": 0.10,
        "Cr": 0.10,
        "Mn": 0.10,
        "Co": 0.10,
        "Zn": 0.10,
        "Cu": 0.10,
        "NH4OH": 0.15,
        "NaCi": 0.15,
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
experiment = Experiment(
    well_volume=2.5,
    cleaning_station_volume=6,
    openTron_IP="100.67.86.197",
    arduino_usb_name="CH340",
)
experiment.arduino.set_temperature(1, 35)
# experiment.cleaning(3)
# experiment.cleaning(4)


logging.info("Sleep 600 seconds to heat up the well plate to 35C")
time.sleep(300)
# experiment.arduino.dispense_ml(pump=1, volume=2)
# experiment.arduino.dispense_ml(pump=2, volume=2)
# experiment.arduino.dispense_ml(pump=3, volume=5)
# experiment.arduino.dispense_ml(pump=4, volume=4)
# experiment.arduino.dispense_ml(pump=3, volume=4)
# experiment.arduino.dispense_ml(pump=4, volume=4)
# experiment.arduino.dispense_ml(pump=3, volume=4)

# # Clean the well
# experiment.cleaning(well_number=11, sleep_time=0.1)

# # Dispense electrolyte
# experiment.dispense_electrolyte(
#     volume=3,
#     chemical="KOH",
#     well_number=11,
# )

# experiment.initiate_potentiostat_admiral()
# # Perform electrochemical testing
# experiment.perform_electrochemical_testing(well_number=11)

# # Disconnect admiral potentiostat
# experiment.close_potentiostat_admiral()

# # Clean the well
# experiment.cleaning(well_number=11, sleep_time=0, use_acid=False)

# # Set timestamp_end of metadata
# experiment.metadata.loc[0, "timestamp_end"] = datetime.now().strftime(
#     "%Y-%m-%d %H:%M:%S"
# )
# # Set status of metadata
# experiment.metadata.loc[0, "status_of_run"] = "success"

# # Save metadata
# experiment.save_metadata()
experiment.__del__()

# tid = [2,10,30,60,90]

logging.info(f"\n\n\nStarting experiment")
experiment = Experiment(
    well_volume=2.5,
    cleaning_station_volume=6,
    openTron_IP="100.67.86.197",
    arduino_usb_name="CH340",
)
experiment.arduino.set_temperature(1, 35)
corrected_potential_10mA = experiment.run_experiment(
    chemicals_to_mix=chemicals_to_mix[0], # XXX Change this to match chemicals_to_mix
    dispense_ml_electrolyte=3,
    electrodeposition_time=60, # XXX Change this to 2, 10, 30, 60, 90
    electrodeposition_temperature=35,
    chemical_ultrasound_mixing_time=30,
    chemical_rest_time=300,
)
experiment.arduino.set_temperature(1, 0)
experiment.__del__()
logging.info(f"Done with experiment \n\n\n")

print("Done with experiments\n")
