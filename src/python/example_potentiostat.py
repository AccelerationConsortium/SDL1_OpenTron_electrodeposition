import logging
from datetime import datetime
from potentiostat_admiral_wrapper import PotentiostatAdmiralWrapper
import sys

# Folder where data and log-file will be saved
DATA_PATH = ""

# Initialize logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(DATA_PATH + "example_potentiostat.log", mode="a"),
        logging.StreamHandler(sys.stdout),
    ],
)
time_now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")


my_experiment = PotentiostatAdmiralWrapper()
my_experiment.runEISPotentiostatic(100000, 1000, 10, 0.001, 0.1)
