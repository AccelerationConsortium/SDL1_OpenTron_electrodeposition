import logging
from datetime import datetime
import sys
from admiral import AdmiralSquidstatWrapper

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


my_experiment = AdmiralSquidstatWrapper(port="COM5", instrument_name="Plus1894")
my_experiment.setup_EIS_potentiostatic(10000, 1000, 10, 0, 0.1, 1)
ac_data, dc_data = my_experiment.get_data()
my_experiment.close_experiment()

print("AC data:")
print(ac_data)
print("DC data:")
print(dc_data)
