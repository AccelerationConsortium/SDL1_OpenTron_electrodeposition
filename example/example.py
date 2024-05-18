from pathlib import Path
import logging
import sys
import time
from python.ardu import Arduino
from python.config import Config
from autoprobe.measurement import run_EIS_and_get_conductivity
from autoprobe.tool import get_measurement_number
import datetime
import pandas as pd


package_root = Path(__file__).parents[1]
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            Path.joinpath(package_root, "data", "peltier.log"), mode="a"
        ),
        logging.StreamHandler(sys.stdout),
    ],
)

robot = Arduino(config=Config().robot)


PUMP_NUM = {"ZnCl2": 0, "Zn(ClO4)2": 3, "water": 4, "Zn(BF4)2": 7}
LIQUID_COST = {"ZnCl2": 0.89, "Zn(ClO4)2": 3.03, "water": 0.006, "Zn(BF4)2": 15}


def run_experiment(volumes: dict, temperature: float):
    """Run the experiment

    Args:
        volumes (dict): Volume of liquids to be mixed
        temperature (float): Temperature at which the measurement made


    Returns:
        float: Conductivity and cost
    """
    robot.set_temperature(temperature)
    robot.clean_cell(4, 1.5)
    robot.clean_cell(4, 1.5)
    volume_dict = dict((PUMP_NUM[key], value) for (key, value) in volumes.items())
    robot.mix_liquids(volume_dict)

    logging.info("Waiting for mixing")
    time.sleep(300)
    robot.transfer_liquid(15)
    count = 0
    while count < 100:
        robot.get_temp_pb1()
        robot.get_temp_pb2()
        count += 1
        time.sleep(1)
    file_path = package_root.joinpath("data")
    measurement_number = get_measurement_number()
    text = "_".join(key + f"{value}" for key, value in volumes.items())
    cond = run_EIS_and_get_conductivity(
        file_path,
        init_freq=100000.0,
        final_freq=1,
        pts_per_decade=10,
        dc=0.0,
        ac=0.0001,
        galvanostat=True,
        file_name="Zn_electrolytes",
        group_name=f"Zn_electrolytes_{measurement_number}_{text}_temp{temperature}",
        cell_constant=1.373,
        is_save_data=True,
    )

    time.sleep(2)
    robot.clean_cell(4, 1.5)
    cost = float(sum([(LIQUID_COST[key] * value) for (key, value) in volumes.items()]))
    return {"conductivity": cond, "cost": cost}


def check_temp(target, process, comment):
    robot.set_temperature_peltier(target)
    start_time = datetime.datetime.now()
    for i in range(900):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        temp_reading = robot.get_temp_peltier()
        # output = robot.get_output_peltier()
        # setpoint = robot.get_setpoint()
        temperatures = pd.DataFrame(
            [
                [
                    current_time,
                    (now - start_time).seconds,
                    process,
                    target,
                    temp_reading,
                    process,
                    comment,
                ]
            ],
        )
        temperatures.to_csv(
            "temperatures_peltier_tuning.csv", mode="a", header=False, index=False
        )
        time.sleep(1)


targets = [15, 25, 35, 45, 35, 25, 15]
processes = ["heating", "heating", "heating", "cooling", "cooling", "cooling"]
comment = "pid_200_0.4_8_single-temp"
for i in range(len(targets)):
    check_temp(targets[i], processes[i], comment)

# robot.drain_cell(15)


# run_experiment({"Zn(BF4)2": 0.3, "Zn(ClO4)2": 0.9, "ZnCl2": 0.0, "water": 0.3}, temperature=25)
