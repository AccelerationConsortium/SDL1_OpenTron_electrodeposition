from ardu import Arduino
import logging
from datetime import datetime
import sys
import time

# Folder where data and log-file will be saved
DATA_PATH = ""
# ARDUINO_NAME = "CH340"  # Arduino name on Windows
ARDUINO_NAME = "USB Serial"  # Arduino name on Mac

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

# Initiate the robot
robot = Arduino(
    arduino_search_string=ARDUINO_NAME,  # Change string to match arduino name
    list_of_cartridges=[
        0,
        1,
    ],  # List of cartridges, where len(list) = number of cartridges
    list_of_pump_relays=[0, 1, 2, 3, 4, 5],  # Pumps connected to which relays
    list_of_ultrasonic_relays=[6, 7],  # Ultrasonic connected to which relays
    pump_slope={0: 2.05, 1: 2.13, 2: 1.93, 3: 2.0263, 4: 2.0263, 5: 2.0263},
    pump_intercept={0: 0.082, 1: 0.058, 2: 0.0686, 3: 0.0607, 4: 0.0607, 5: 0.0607},
)


###############################################################################
# Workflow
###############################################################################
# Set temperature to 0 degrees for cartridge 0
robot.set_temperature(0, 0)

# # Set temperature to 35 degrees for cartridge 1
robot.set_temperature(1, 35)

# # Set ultrasound on for cartridge 0 for 1 seconds
robot.set_ultrasound_on(0, 1)

# # Set ultrasound on for cartridge 1 for 1 seconds
robot.set_ultrasound_on(1, 1)

# Set all pumps on, one at a time, for 5 seconds
robot.set_pump_on(0, 1)
robot.set_pump_on(1, 1)
robot.set_pump_on(2, 1)
robot.set_pump_on(3, 1)
robot.set_pump_on(4, 1)
robot.set_pump_on(5, 1)
