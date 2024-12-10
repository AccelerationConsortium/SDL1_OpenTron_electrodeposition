import logging
from datetime import datetime
import sys
from experiment import Experiment
import time
from admiral import AdmiralSquidstatWrapper

port = "COM5"
instrument_name = "Plus1894"


# Folder where data and log-file will be saved
DATA_PATH = ""
NAME_OF_ARDUINO = "CH340"  # Arduino name on Windows for auto finding COM port
chemicals_to_mix = [
    {
        "Ni": 0,
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
        "Ni": 0.5,
        "Fe": 0.5,
        "Cr": 0.0,
        "Mn": 0.0,
        "Co": 0.0,
        "Zn": 0.0,
        "Cu": 0.0,
        "NH4OH": 0.0,
        "NaCi": 0.0,
    },
    {
        "Ni": 0.5,
        "Fe": 0.5,
        "Cr": 0.0,
        "Mn": 0.0,
        "Co": 0.0,
        "Zn": 0.0,
        "Cu": 0.0,
        "NH4OH": 0.0,
        "NaCi": 0.0,
    },
    {
        "Ni": 0.5,
        "Fe": 0.5,
        "Cr": 0.0,
        "Mn": 0.0,
        "Co": 0.0,
        "Zn": 0.0,
        "Cu": 0.0,
        "NH4OH": 0.0,
        "NaCi": 0.0,
    },
    {
        "Ni": 0.5,
        "Fe": 0.5,
        "Cr": 0.0,
        "Mn": 0.0,
        "Co": 0.0,
        "Zn": 0.0,
        "Cu": 0.0,
        "NH4OH": 0.0,
        "NaCi": 0.0,
    },
    {
        "Ni": 0.11,
        "Fe": 0.11,
        "Cr": 0.11,
        "Mn": 0.11,
        "Co": 0.11,
        "Zn": 0.11,
        "Cu": 0.11,
        "NH4OH": 0.11,
        "NaCi": 0.11,
    },
    {
        "Ni": 0.11,
        "Fe": 0.11,
        "Cr": 0.11,
        "Mn": 0.11,
        "Co": 0.11,
        "Zn": 0.11,
        "Cu": 0.11,
        "NH4OH": 0.11,
        "NaCi": 0.11,
    },
    {
        "Ni": 0.11,
        "Fe": 0.11,
        "Cr": 0.11,
        "Mn": 0.11,
        "Co": 0.11,
        "Zn": 0.11,
        "Cu": 0.11,
        "NH4OH": 0.11,
        "NaCi": 0.11,
    },
    {
        "Ni": 0.11,
        "Fe": 0.11,
        "Cr": 0.11,
        "Mn": 0.11,
        "Co": 0.11,
        "Zn": 0.11,
        "Cu": 0.11,
        "NH4OH": 0.11,
        "NaCi": 0.11,
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

# Initialize Admiral potentiostat
logging.info(f"Initiating potentiostat on port {port} with name {instrument_name}")
admiral = AdmiralSquidstatWrapper(port=port, instrument_name=instrument_name)

# Setting temperature on test cell/well (and making an object to do so)
experiment = Experiment(
    well_volume=2.5,
    cleaning_station_volume=6,
    openTron_IP="100.67.86.197",
    arduino_usb_name="CH340",
)
experiment.arduino.set_temperature(1, 35)

logging.info("Sleep 600 seconds to heat up the well plate to 35C")
time.sleep(300)
#####################
# This section is just for a homing run and not necessary for the experiment
# once all pumps are primed and once the well is 35C
#####################

# ### Priming of pumps
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

# Loop through all the experiments
for i in range(len(chemicals_to_mix)):
    logging.info(f"Starting experiment {i+1}")

    experiment = Experiment(
        well_volume=2.5,
        cleaning_station_volume=6,
        openTron_IP="100.67.86.197",
        arduino_usb_name="CH340",
        admiral=admiral,
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

logging.info("Closing admiral potentiostat connection")
admiral.close_experiment()

logging.info("Done with experiment \n\n\n")

print("Done with experiments\n")
