from .ardu import Arduino
import logging
from datetime import datetime
import sys
import time
from .experiment import Experiment

# Folder where data and log-file will be saved
DATA_PATH = ""
NAME_OF_ARDUINO = "CH340"

experiment = Experiment(
    well_volume=2.5,
    cleaning_station_volume=15,
    openTron_IP="100.67.86.197",
    arduino_usb_name="CH340",
)

# Return potential at 10 mA/cm^2s
print("Done\n")
