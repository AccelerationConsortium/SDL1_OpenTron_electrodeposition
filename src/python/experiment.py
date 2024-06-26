from ardu import Arduino
import logging
from datetime import datetime
import sys
import json
import os
from opentronwrapper import opentronsClient
from parameters import (
    labware_paths,
    wells,
    pipetteable_chemicals,
    labware_tools,
    pipette_tips,
)

LOGGER = logging.getLogger(__name__)
DATA_PATH = os.getcwd()
OPENTRON_PIPETTE = "p1000_single_gen2"
path = os.path.join(DATA_PATH, "src", "opentron_labware", "nis_4_tiprack_1ul.json")


class Experiment:

    def __init__(
        self,
        vial_volume: float = 2.0,
        cleaning_station_volume: float = 5,
        openTron_IP: str = "100.67.86.197",
        openTron_pipette_name: str = "p1000_single_gen2",
    ):
        self.cleaning_station_volume = cleaning_station_volume
        self.vial_volume = vial_volume

        # Initiate the arduino
        self.arduino = Arduino()
        # Initiate the openTron
        self.openTron = opentronsClient(openTron_IP)

    def initiate_openTron(self):
        # Tools
        path = os.path.join(DATA_PATH, labware_paths["nistall_4_tiprack_1ul"])
        self.labware_tool_rack = self.read_json(path)
        self.labware_tool_rack = self.openTron.loadCustomLabware(
            dicLabware=self.labware_tool_rack, intSlot=10
        )

        # Vials with solutions
        path = os.path.join(DATA_PATH, labware_paths["nis_8_reservoir_25000ul"])
        self.labware_stock_solutions1 = self.read_json(path)
        self.labware_stock_solutions1 = self.openTron.loadCustomLabware(
            dicLabware=self.labware_stock_solutions1, intSlot=4
        )

        # Vials with solutions
        path = os.path.join(DATA_PATH, labware_paths["nis_8_reservoir_25000ul"])
        self.labware_stock_solutions2 = self.read_json(path)
        self.labware_stock_solutions2 = self.openTron.loadCustomLabware(
            dicLabware=self.labware_stock_solutions2, intSlot=5
        )

        # Well plate where the testing takes place
        path = os.path.join(DATA_PATH, labware_paths["nis_15_wellplate_3895ul"])
        self.labware_well_plate = self.read_json(path)
        self.labware_well_plate = self.openTron.loadCustomLabware(
            dicLabware=self.labware_well_plate, intSlot=9
        )

        # Cleaning cell for the openTron tools
        path = os.path.join(DATA_PATH, labware_paths["nis_2_wellplate_30000ul"])
        self.labware_cleaning_cartridge = self.read_json(path)
        self.labware_cleaning_cartridge = self.openTron.loadCustomLabware(
            dicLabware=self.labware_cleaning_cartridge, intSlot=3
        )
        # Load pipette tip rack
        self.labware_pipette_tips = self.openTron.loadLabware(
            1, "opentrons_96_tiprack_1000ul"
        )

    # Read JSON
    def read_json(path: str) -> dict:
        with open(path, encoding="utf8") as f:
            return json.load(f)

    def get_temperature(self, cartridge_number: float):
        pass

    def set_temperature(self, temperature: float, cartridge_number: int):
        # Check that temperature is a positive number
        if temperature < 0:
            raise ValueError("Temperature should be a positive number")

        # Check that cartridge_number is a positive number
        if cartridge_number < 0:
            raise ValueError("Cartridge number should be a positive number")

        pass

    def clean_cell(self, vial_number: int, volume: float):
        pass

    def dispense_to_vial(self, vial_number: int, volume: float):
        # Check if the vial_number is between 0 and 1000
        if vial_number < 0 or vial_number > 1000:
            raise ValueError("Vial number should be between 0 and 1000")

        # Check if the volume is between 0 and 100
        if volume < 0 or volume > 100:
            raise ValueError("Volume should be between 0 and 100")

        pass

    def dispense_peristaltic(self, pump_number: int, volume: float):
        # Check if the pump_number is between 0 and 7
        if pump_number < 0 or pump_number > 7:
            raise ValueError("Pump number should be between 0 and 7")

        # Check if the volume is between 0 and 100
        if volume < 0 or volume > 100:
            raise ValueError("Volume should be between 0 and 100")

        pass

    def run_experiment(self):
        # Home robot
        self.openTron.homeRobot()
