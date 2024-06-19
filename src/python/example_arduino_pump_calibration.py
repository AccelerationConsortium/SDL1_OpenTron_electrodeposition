from ardu import Arduino
import logging
from datetime import datetime
import sys
import time

# Folder where data and log-file will be saved
DATA_PATH = ""

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(DATA_PATH + "example_arduino_pump_calibration.log", mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
time_now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

# Initiate the robot
robot = Arduino(
    arduino_search_string="CH340",  # Change string to match arduino name
    list_of_cartridges=[
        0,
        1,
    ],  # List of cartridges, where len(list) = number of cartridges
    list_of_pump_relays=[0, 1, 2, 3, 4, 5],  # Pumps connected to which relays
    list_of_ultrasonic_relays=[6, 7],  # Ultrasonic connected to which relays
)


###############################################################################
# Workflow
###############################################################################
# Write down the weight of dispensed water and tare in between dispensing.
# Repeat for each pump 3 times.
# This can, combined with temparature, be used to calibrate the pumps by
# converting to flow and then making a linear regression to find
# the slope and intercept for each pump.

list_of_times = [0.5, 1, 2, 5, 10, 15]
# Ask for user input
pump_number = int(input("Enter pump number to calibrate: "))
for seconds in list_of_times:
    input(f"Press enter to dispense {seconds} seconds: ")
    robot.set_pump_on(pump_number, seconds)

print("Calibration done")