from ardu import Arduino
import logging
from datetime import datetime
import sys

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

robot = Arduino(arduino_search_string="USB Serial")  # Name of your arduino
# temperature0 = robot.get_temperature0()
# temperature1 = robot.get_temperature1()

# temperature0_ambient = robot.get_temperature0_ambient()
# temperature1_ambient = robot.get_temperature1_ambient()

# Test relay on/off
robot.set_relay_on_time(4, 2)
robot.set_relay_on_time(5, 3)
