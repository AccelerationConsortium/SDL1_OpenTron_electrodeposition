import logging
import time
from datetime import datetime
import sys
import json
import smtplib
from email.mime.text import MIMEText
import json
import os
import pandas as pd
from biologic import connect, BANDWIDTH, I_RANGE
from biologic.techniques.cv import CVTechnique, CVParams, CVStep
from biologic.techniques.ocv import OCVTechnique, OCVParams
from biologic.techniques.peis import PEISTechnique, PEISParams, SweepMode
from biologic.techniques.cp import CPTechnique, CPParams, CPStep, Parameter
from ardu import Arduino
from admiral import AdmiralSquidstatWrapper
from opentronsHTTPAPI_clientBuilder import opentronsClient
from parameters import (
    labware_paths,
    wells,
    pipetteable_chemicals,
    labware_tools,
    pipette_tips,
    pump_slope,
    pump_intercept,
    tool_x_offset,
    tool_y_offset,
    tool_z_offset,
    tool_z_dropoff,
    pipetteable_chemical_racks,
    sample_surface_area,
    current_at_sample,
    OHMIC_CORRECTION_FACTOR,
    peristaltic_pump_content,
)

LOGGER = logging.getLogger(__name__)
DATA_PATH = os.getcwd()
path = os.path.join(DATA_PATH, "src", "opentron_labware", "nis_4_tiprack_1ul.json")


class Experiment:

    def __init__(
        self,
        well_volume: float = 3.0,
        cleaning_station_volume: float = 6,
        openTron_IP: str = "100.67.86.197",
        openTron_pipette_name: str = "p1000_single_gen2",
        arduino_usb_name: str = "CH340",
    ):
        self.cleaning_station_volume = cleaning_station_volume
        self.well_volume = well_volume
        self.openTron_pipette_name = openTron_pipette_name
        self.openTron_IP = openTron_IP
        self.arduino_usb_name = arduino_usb_name
        self.sample_surface_area = sample_surface_area
        self.deposition_current = current_at_sample

        # Initiate the arduino
        self.initiate_arduino()
        # Initiate the openTron
        self.initiate_openTron()

        # Read unique id from uid_run_number.txt
        with open("uid_run_number.txt", "r") as f:
            self.unique_id = int(f.read())

        # Increase the unique id by 1
        self.unique_id = self.unique_id + 1

        # Update the unique id in the file
        with open("uid_run_number.txt", "w") as f:
            f.write(str(self.unique_id))

        # Make a pandas dataframe to store metadata with the columns
        self.metadata = pd.DataFrame(
            columns=[
                "unique_id",
                "well_number",
                "chemicals_to_mix",
                "total_volume [ml]",
                "deposition_current [A]",
                "electrodeposition_time [s]",
                "sample_surface_area",
                "ohmic_resistance [ohm]",
                "well_temperature_during_deposition [C]",
                "well_temperature_during_electrochemical_measurements [C]",
                "potential_at_10mAcm2 [V]",
                "corrected_potential_at_10mAcm2 [V]",
                "timestamp_start",
                "timestamp_end",
                "status_of_run",
                "electrodeposition_temperature_setpoint [C]",
                "chemical_ultrasound_mixing_time [s]",
                "chemical_rest_time [s]",
            ]
        )
        # Update the metadata with the unique id
        self.metadata.loc[0, "unique_id"] = self.unique_id

        # Set the timestamp for the start of the experiment
        self.metadata.loc[0, "timestamp_start"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Get the well number
        self.well_number = self.load_well_number()

        self.save_metadata()

        # Load the chemicals left from the last run
        try:
            with open("chemicals_left.txt", "r") as f:
                self.chemical_volumes_left = json.load(f)
        except FileNotFoundError:
            LOGGER.error("Error: 'chemicals_left.txt' file not found.")
            raise RuntimeError("Error: 'chemicals_left.txt' file not found.")

        self.electrode_is_on_pipette = False

    def initiate_arduino(
        self,
        ARDUINO_NAME: str = "CH340",
        pump_intercept: dict = pump_intercept,
        pump_slope: dict = pump_slope,
        list_of_cartridges: list = [0, 1],
        list_of_pump_relays=[0, 1, 2, 3, 4, 5],  # Pumps connected to which relays
        list_of_ultrasonic_relays=[6, 7],  # Ultrasonic connected to which relays
    ) -> None:
        """Initiate the arduino

        Args:
            ARDUINO_NAME (str, optional): Name of the arduino. Defaults to "CH340".
            pump_intercept (dict, optional): Intercept for the pumps. Defaults to pump_intercept.
            pump_slope (dict, optional): Slope for the pumps. Defaults to pump_slope.
            list_of_cartridges (list, optional): List of cartridges. Defaults to [0, 1].
            list_of_pump_relays (list, optional): Pumps connected to which relays. Defaults to [0, 1, 2, 3, 4, 5].
            list_of_ultrasonic_relays (list, optional): Ultrasonic connected to which relays. Defaults to [6, 7].
        """
        LOGGER.info(f"Initiating arduino with usb nam: {ARDUINO_NAME}")
        self.arduino = Arduino(
            arduino_search_string=ARDUINO_NAME,  # Change string to match arduino name
            list_of_cartridges=list_of_cartridges,  # List of cartridges, where len(list) = number of cartridges
            list_of_pump_relays=list_of_pump_relays,  # Pumps connected to which relays
            list_of_ultrasonic_relays=list_of_ultrasonic_relays,  # Ultrasonic connected to which relays
            pump_slope=pump_slope,  # dict of pump slopes: a in y = ax + b
            pump_intercept=pump_intercept,  # dict of pump intercepts: b in y = ax + b
        )

    def initiate_openTron(self):
        try:
            self.openTron = opentronsClient(self.openTron_IP)
        except Exception as e:
            LOGGER.error(f"Could not connect to the openTron: {e}")

        # add pipette
        self.openTron.loadPipette(
            strPipetteName=self.openTron_pipette_name, strMount="right"
        )

        # Tools
        path = os.path.join(DATA_PATH, labware_paths["nistall_4_tiprack_1ul"])
        LOGGER.debug(f"Path given to read_json(): {path}")
        self.labware_tool_rack = self.read_json(path)
        self.labware_tool_rack = self.openTron.loadCustomLabware(
            dicLabware=self.labware_tool_rack,
            intSlot=10,
        )

        # Vials with solutions
        path = os.path.join(DATA_PATH, labware_paths["nis_8_reservoir_25000ul"])
        self.labware_stock_solutions1 = self.read_json(path)
        self.labware_stock_solutions1 = self.openTron.loadCustomLabware(
            dicLabware=self.labware_stock_solutions1,
            intSlot=11,  # Remember to change in the parameters.py if slot is changed
        )

        # Vials with solutions
        path = os.path.join(DATA_PATH, labware_paths["nis_8_reservoir_25000ul"])
        self.labware_stock_solutions2 = self.read_json(path)
        self.labware_stock_solutions2 = self.openTron.loadCustomLabware(
            dicLabware=self.labware_stock_solutions2,
            intSlot=7,  # Remember to change in the parameters.py if slot is changed
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
            intSlot=1, strLabwareName="opentrons_96_tiprack_1000ul"
        )

    def read_json(self, path: str) -> dict:
        with open(path, encoding="utf8") as f:
            return json.load(f)

    def initiate_potentiostat_admiral(
        self, port: str = "COM5", instrument_name: str = "Plus1894"
    ):
        """Initiate the potentiostat

        Args:
            port (str, optional): Port of the potentiostat. Defaults to "COM5".
            instrument_name (str, optional): Name of the potentiostat. Defaults to "Plus1894".
        """
        LOGGER.info(
            f"Initiating potentiostat on port {port} with name {instrument_name}"
        )
        self.admiral = AdmiralSquidstatWrapper(
            port=port, instrument_name=instrument_name
        )

    def correct_for_ohmic_resistance(
        self,
        df: pd.DataFrame,
        ohmic_resistance: float,
        ohmic_correction_factor: float = OHMIC_CORRECTION_FACTOR,
    ) -> pd.DataFrame:
        """Correct potential for ohmic resistance

        Args:
            df (pd.DataFrame): Dataframe containing the data to correct. Must contain a
            column named "Working Electrode Current [A]" and a column named "Working Electrode Voltage [V]".
            ohmic_resistance (float): Ohmic resistance in ohm

        Returns:
            pd.DataFrame: Dataframe with corrected potential
        """
        LOGGER.info("Correcting for ohmic resistance")
        df["Corrected Working Electrode Voltage [V]"] = (
            df["Working Electrode Voltage [V]"]
            - ohmic_correction_factor
            * ohmic_resistance
            * df["Working Electrode Current [A]"]
        )
        return df

    def store_data_admiral(
        self, dc_data: pd.DataFrame, ac_data: pd.DataFrame, file_name: str
    ):
        """Store data from the potentiostat in a csv file

        Args:
            dc_data (pd.DataFrame): Data from the potentiostat
            ac_data (pd.DataFrame): Data from the potentiostat
            file_name (str): Name of the file to store the data in without the file extension
        """

        if dc_data is not None:
            LOGGER.debug(f"Storing DC data in {file_name} dc_data.csv")
            dc_data.to_csv(file_name + " dc_data.csv", sep=",")
        if ac_data is not None:
            LOGGER.debug(f"Storing AC data in {file_name} ac_data.csv")
            ac_data.to_csv(file_name + " ac_data.csv", sep=",")

    def close_potentiostat_admiral(self):
        """Close the potentiostat"""
        LOGGER.info("Closing admiral potentiostat connection")
        self.admiral.close_experiment()

    def perform_potentiostat_measurements(self):
        ### 0 - Electrochemical Activation
        LOGGER.info("Performing electrochemical test: 0 - Electrochemical activation")
        self.admiral.setup_constant_current(
            holdAtCurrent=0.2 * self.sample_surface_area,
            samplingInterval=0.05,
            duration=60,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        self.admiral.clear_data()
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 0 CP 200 mA cm-2"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)

        ### 1 - Perform CV
        LOGGER.info("Performing electrochemical test: 1 - Cyclic voltammetry")
        self.admiral.setup_cyclic_voltammetry(
            startVoltage=0.8,
            firstVoltageLimit=2.3,
            secondVoltageLimit=0.8,
            endVoltage=0.8,
            scanRate=0.2,
            samplingInterval=0.05,
            cycles=25,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 1 CV 25x 200mV s-1"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

        ### 2 - Perform CV
        LOGGER.info("Performing electrochemical test: 2 - Cyclic voltammetry")
        self.admiral.setup_cyclic_voltammetry(
            startVoltage=0.8,
            firstVoltageLimit=2.3,
            secondVoltageLimit=0.8,
            endVoltage=0.8,
            scanRate=0.01,
            samplingInterval=0.2,
            cycles=2,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 2 CV 2x 10mV s-1"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

        ### 3 - Perform EIS
        LOGGER.info(
            "Performing electrochemical test: 3 - Electrochemical impedance spectroscopy"
        )
        self.admiral.setup_EIS_potentiostatic(
            start_frequency=500000,
            end_frequency=1,
            points_per_decade=10,
            voltage_bias=1.5,
            voltage_amplitude=0.01,
            number_of_runs=0,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 3 EIS"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        # Find ohmic resistance
        self.ohmic_resistance = self.find_ohmic_resistance(
            df=ac_data,
            column_name_imag="Imaginary Impedance",
            column_name_real="Real Impedance",
        )
        self.admiral.clear_data()

        # Updata metadata
        self.metadata.loc[0, "ohmic_resistance [ohm]"] = self.ohmic_resistance
        self.save_metadata()

        ### 4 - Perform CP at 100 mA/cm^2
        LOGGER.info(
            "Performing electrochemical test: 4 - Constant current at 100 mA/cm^2"
        )
        self.admiral.setup_constant_current(
            holdAtCurrent=0.1 * self.sample_surface_area,
            samplingInterval=0.05,
            duration=70,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Correct DC data for ohmic resistance
        dc_data = self.correct_for_ohmic_resistance(
            df=dc_data,
            ohmic_resistance=self.ohmic_resistance,
            ohmic_correction_factor=OHMIC_CORRECTION_FACTOR,
        )
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 4 CP 100 mA cm-2"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

        ### 5 - Perform CP at 50 mA/cm^2
        LOGGER.info(
            "Performing electrochemical test: 5 - Constant current at 50 mA/cm^2"
        )
        self.admiral.setup_constant_current(
            holdAtCurrent=0.05 * self.sample_surface_area,
            samplingInterval=0.05,
            duration=70,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Correct DC data for ohmic resistance
        dc_data = self.correct_for_ohmic_resistance(
            df=dc_data,
            ohmic_resistance=self.ohmic_resistance,
            ohmic_correction_factor=OHMIC_CORRECTION_FACTOR,
        )
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 5 CP 50 mA cm-2"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

        ### 6 - Perform CP at 20 mA/cm^2
        LOGGER.info(
            "Performing electrochemical test: 6 - Constant current at 20 mA/cm^2"
        )
        self.admiral.setup_constant_current(
            holdAtCurrent=0.02 * self.sample_surface_area,
            samplingInterval=0.05,
            duration=70,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Correct DC data for ohmic resistance
        dc_data = self.correct_for_ohmic_resistance(
            df=dc_data,
            ohmic_resistance=self.ohmic_resistance,
            ohmic_correction_factor=OHMIC_CORRECTION_FACTOR,
        )
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 6 CP 20 mA cm-2"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

        ### 7 - Perform CP at 10 mA/cm^2
        LOGGER.info(
            "Performing electrochemical test: 7 - Constant current at 10 mA/cm^2"
        )
        self.admiral.setup_constant_current(
            holdAtCurrent=0.01 * self.sample_surface_area,
            samplingInterval=0.05,
            duration=70,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Correct DC data for ohmic resistance
        dc_data = self.correct_for_ohmic_resistance(
            df=dc_data,
            ohmic_resistance=self.ohmic_resistance,
            ohmic_correction_factor=OHMIC_CORRECTION_FACTOR,
        )
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 7 CP 10 mA cm-2"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

        # Find average ohmic corrected potential at 10 mA/cm^2 for the last third of the data
        self.metadata.loc[0, "potential_at_10mAcm2 [V]"] = (
            dc_data["Working Electrode Voltage [V]"].tail(int(len(dc_data) / 3)).mean()
        )
        self.metadata.loc[0, "corrected_potential_at_10mAcm2 [V]"] = (
            dc_data["Corrected Working Electrode Voltage [V]"]
            .tail(int(len(dc_data) / 3))
            .mean()
        )
        self.save_metadata()

        # 8 - Perform CP at 5 mA/cm^2
        LOGGER.info(
            "Performing electrochemical test: 8 - Constant current at 5 mA/cm^2"
        )
        self.admiral.setup_constant_current(
            holdAtCurrent=0.005 * self.sample_surface_area,
            samplingInterval=0.05,
            duration=70,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()

        # Correct DC data for ohmic resistance
        dc_data = self.correct_for_ohmic_resistance(
            df=dc_data,
            ohmic_resistance=self.ohmic_resistance,
            ohmic_correction_factor=OHMIC_CORRECTION_FACTOR,
        )
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 8 CP 5 mA cm-2"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

        ### 9 - Perform CP at 2 mA/cm^2
        LOGGER.info(
            "Performing electrochemical test: 9 - Constant current at 2 mA/cm^2"
        )
        self.admiral.setup_constant_current(
            holdAtCurrent=0.002 * self.sample_surface_area,
            samplingInterval=0.05,
            duration=70,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Correct DC data for ohmic resistance
        dc_data = self.correct_for_ohmic_resistance(
            df=dc_data,
            ohmic_resistance=self.ohmic_resistance,
            ohmic_correction_factor=OHMIC_CORRECTION_FACTOR,
        )
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 9 CP 2 mA cm-2"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

        ### 10 - Perform CP at 1 mA/cm^2
        LOGGER.info(
            "Performing electrochemical test: 10 - Constant current at 1 mA/cm^2"
        )
        self.admiral.setup_constant_current(
            holdAtCurrent=0.001 * self.sample_surface_area,
            samplingInterval=0.05,
            duration=70,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Correct DC data for ohmic resistance
        dc_data = self.correct_for_ohmic_resistance(
            df=dc_data,
            ohmic_resistance=self.ohmic_resistance,
            ohmic_correction_factor=OHMIC_CORRECTION_FACTOR,
        )
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 10 CP 1 mA cm-2"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

        ### 11 - Perform CV
        LOGGER.info("Performing electrochemical test: 11 - Cyclic voltammetry")
        self.admiral.setup_cyclic_voltammetry(
            startVoltage=0.8,
            firstVoltageLimit=2.3,
            secondVoltageLimit=0.8,
            endVoltage=0.8,
            scanRate=0.01,
            samplingInterval=0.2,
            cycles=2,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Correct DC data for ohmic resistance
        dc_data = self.correct_for_ohmic_resistance(
            df=dc_data,
            ohmic_resistance=self.ohmic_resistance,
            ohmic_correction_factor=OHMIC_CORRECTION_FACTOR,
        )
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 11 CV 2x 10mV s-1"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

        ### 11 - Perform CV to reduce the surface again so that it looks nice and not rusty
        LOGGER.info("Performing electrochemical test: 11 - Cyclic voltammetry")
        self.admiral.setup_cyclic_voltammetry(
            startVoltage=0.8,
            firstVoltageLimit=-0.2,
            secondVoltageLimit=0,
            endVoltage=-0.2,
            scanRate=0.01,
            samplingInterval=0.2,
            cycles=2,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        # Correct DC data for ohmic resistance
        dc_data = self.correct_for_ohmic_resistance(
            df=dc_data,
            ohmic_resistance=self.ohmic_resistance,
            ohmic_correction_factor=OHMIC_CORRECTION_FACTOR,
        )
        # Save data
        filepath = DATA_PATH + "\\data\\" + str(self.unique_id) + " 12 CV 2x 10mV s-1"
        self.store_data_admiral(dc_data=dc_data, ac_data=ac_data, file_name=filepath)
        self.admiral.clear_data()

    def send_mail(self, msg: str, title: str, receivers: list):
        """Send an email to the specified receivers

        Args:
            msg (str): Message to send
            title (str): Title of the email
            receivers (list): List of receivers email addresses
        """
        smtp = smtplib.SMTP("smtp.simply.com", port=587)

        sender = "robot@dosan.dk"

        message = MIMEText(f"{msg}")
        message["Subject"] = title
        message["From"] = "robot@dosan.dk"
        message["To"] = "Nis"

        try:
            smtp.ehlo()  # send the extended hello to our server
            smtp.starttls()  # tell server we want to communicate with TLS encryption
            smtp.login("robot@dosan.dk", "abc12345678")  # login to our email server
            smtp.sendmail(sender, receivers, message.as_string())
            smtp.quit()  # close the connection
            logging.info("Successfully sent email")
        except Exception:
            logging.warning("Error: unable to send email")

    def perform_potentiostat_electrodeposition(self, seconds: int = 10):
        """Perform electrodeposition of the sample

        Args:
            seconds (int, optional): Duration of the electrodeposition in seconds. Defaults to 10.
        """
        LOGGER.info(
            f"Potentiostat performing electrodeposition of the sample with {self.deposition_current} A for {seconds} seconds"
        )

        # Get temperature of the well
        self.metadata.loc[0, "well_temperature_during_deposition [C]"] = (
            self.arduino.get_temperature1()
        )
        LOGGER.info("Making an OCV")
        self.admiral.setup_OCP(duration=120, samplingInterval=0.2)
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        self.admiral.clear_data()
        # Save data
        self.store_data_admiral(
            dc_data=dc_data,
            ac_data=ac_data,
            file_name=DATA_PATH
            + "\\"
            + str(self.unique_id)
            + " -3 OCV scan 1x 10mV s-1",
        )

        # XXX THIS SECTION SHOULD BE REMOVED IN THE FUTURE
        LOGGER.info("Making a cathodic scan")
        self.admiral.setup_cyclic_voltammetry(
            startVoltage=0,  # XXX Can this be OCV somehow?
            firstVoltageLimit=0.5,
            secondVoltageLimit=-10,
            endVoltage=0.5,
            scanRate=0.1,
            samplingInterval=0.2,
            cycles=1,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        self.admiral.clear_data()
        # Save data
        self.store_data_admiral(
            dc_data=dc_data,
            ac_data=ac_data,
            file_name=DATA_PATH
            + "\\"
            + str(self.unique_id)
            + " -2 Cathodic scan 1x 10mV s-1",
        )
        # XXX END OF REMOVABLE SECTION

        LOGGER.info("Performing electrodeposition")
        # Apply constant current for X seconds
        self.admiral.setup_constant_current(
            holdAtCurrent=-self.deposition_current,
            samplingInterval=0.1,
            duration=seconds,
        )
        self.admiral.run_experiment()
        ac_data, dc_data = self.admiral.get_data()
        self.admiral.clear_data()
        # Save data
        self.store_data_admiral(
            dc_data=dc_data,
            ac_data=ac_data,
            file_name=DATA_PATH
            + "\\data\\"
            + str(self.unique_id)
            + " -1 Electrodeposition",
        )

    def emergency_parking_of_electrode(self, well_number: int):
        """Emergency park the electrode"""
        LOGGER.warning("Emergency parking of the electrode")

        # Go straight up from the well
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=20,
            intSpeed=50,  # mm/s
        )
        # Go to cleaning cartridge
        self.openTron.moveToWell(
            strLabwareName=self.labware_cleaning_cartridge,
            strWellName="A2",
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=20,
            intSpeed=50,  # mm/s
        )
        # Go down in well
        self.openTron.moveToWell(
            strLabwareName=self.labware_cleaning_cartridge,
            strWellName="A2",
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=-33,
            intSpeed=10,  # mm/s
        )

        # Flush the electrode in the cleaning station/cartridge
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_H2O"],
            volume=self.cleaning_station_volume,
        )
        # Update chemical volumes left
        self.chemical_volumes_left["Cartridge_H2O"] -= self.cleaning_station_volume

        # Drain
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_Drain"],
            volume=self.cleaning_station_volume + 1,
        )
        # Update chemical volumes left
        self.chemical_volumes_left["Waste"] -= self.cleaning_station_volume

        # Flush with HCl
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_HCl"],
            volume=self.cleaning_station_volume,
        )
        self.chemical_volumes_left["Cartridge_HCl"] -= self.cleaning_station_volume
        self.arduino.set_ultrasound_on(0, 15)

        # Drain
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_Drain"],
            volume=self.cleaning_station_volume + 1,
        )
        # Update chemical volumes left
        self.chemical_volumes_left["Waste"] -= self.cleaning_station_volume

        # Flush with water
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_H2O"],
            volume=self.cleaning_station_volume,
        )
        # Update chemical volumes left
        self.chemical_volumes_left["Cartridge_H2O"] -= self.cleaning_station_volume
        self.arduino.set_ultrasound_on(0, 5)

        # Drain
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_Drain"],
            volume=self.cleaning_station_volume + 1,
        )
        # Update chemical volumes left
        self.chemical_volumes_left["Waste"] -= self.cleaning_station_volume

        # Save the volumes left to file
        self.save_chemical_volumes_left()

        # Go straight up
        self.openTron.moveToWell(
            strLabwareName=self.labware_cleaning_cartridge,
            strWellName="A2",
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=20,
            intSpeed=50,  # mm/s
        )
        # Go to tool rack
        self.openTron.moveToWell(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["OER_electrode"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=tool_x_offset["OER_electrode"],
            fltOffsetY=tool_y_offset["OER_electrode"],
            fltOffsetZ=50,
            intSpeed=50,  # mm/s
        )
        # Drop OER electrode
        self.openTron.dropTip(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["OER_electrode"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="bottom",
            fltOffsetX=tool_x_offset["OER_electrode"],
            fltOffsetY=tool_y_offset["OER_electrode"],
            fltOffsetZ=tool_z_dropoff["OER_electrode"],
            boolHomeAfter=False,
            boolAlternateDropLocation=False,
        )

    def save_chemical_volumes_left(self):
        """Save the volumes of the chemicals left in the stock solutions"""
        LOGGER.debug("Saving the volumes of the chemicals left")

        with open("chemicals_left.txt", "w") as f:
            json.dump(self.chemical_volumes_left, f)

    def perform_potentiostat_reference_measurement(self, string_to_add: str = ""):
        """Perform reference electrode measurement

        Args:
            string_to_add (str, optional): String to add to the file name
                eg. ' after'). Defaults to ''.
        """
        ### Create a CV technique
        LOGGER.info(
            "Performing CV on Biologic potentiostat for reference electrode correction"
        )
        Ei = CVStep(voltage=0, scan_rate=1, vs_initial=False)
        E1 = CVStep(voltage=2, scan_rate=1, vs_initial=False)
        E2 = CVStep(voltage=-0.2, scan_rate=1, vs_initial=False)
        Ef = CVStep(voltage=0, scan_rate=1, vs_initial=False)

        params = CVParams(
            record_every_dE=0.01,
            average_over_dE=False,
            n_cycles=25,
            begin_measuring_i=0.1,
            end_measuring_i=0.5,
            Ei=Ei,
            E1=E1,
            E2=E2,
            Ef=Ef,
            bandwidth=BANDWIDTH.BW_5,
        )

        tech = CVTechnique(params)

        params = PEISParams(
            vs_initial=False,
            initial_voltage_step=0.1,
            duration_step=3,
            record_every_dI=0.01,
            record_every_dT=1,
            correction=False,
            final_frequency=1000,
            initial_frequency=100000,
            amplitude_voltage=0.01,
            average_n_times=3,
            frequency_number=10,
            sweep=SweepMode.Linear,  # Linear or Logarithmic
            wait_for_steady=False,
            bandwidth=BANDWIDTH.BW_5,
        )

        tech2 = PEISTechnique(params)

        break_loop = False
        max_tries = 5
        counter = 0
        while break_loop == False and max_tries > counter:
            LOGGER.info(
                f"Trying to connect to the potentiostat: {counter+1}/{max_tries}"
            )
            try:
                with connect("USB0", force_load=True) as bl:
                    channel = bl.get_channel(2)

                    # Push the technique to the Biologic
                    results = []
                    runner = channel.run_techniques([tech])
                    for result in runner:
                        results.append(result.data)
                    else:
                        time.sleep(1)

                    # make results into a pandas dataframe
                    df = pd.DataFrame(results)
                    LOGGER.debug(f"Dataframe received: {df}")

                    # Save the data
                    filepath = (
                        DATA_PATH
                        + "\\"
                        + str(self.unique_id)
                        + f" Ref CV{string_to_add}.csv"
                    )
                    LOGGER.debug(f"Saving data to {filepath}")
                    df.to_csv(filepath)
                    time.sleep(1)

                    ### Create a EIS technique
                    LOGGER.info(
                        "Performing EIS on Biologic potentiostat for reference electrode correction"
                    )

                    # Push the technique to the Biologic
                    results = []
                    runner = channel.run_techniques([tech2])
                    for result in runner:
                        results.append(result.data.process_data)
                    else:
                        time.sleep(1)

                    # make results into a pandas dataframe
                    df = pd.DataFrame(results)
                    LOGGER.debug(f"Dataframe received: {df}")

                    # Save the data
                    filepath = (
                        DATA_PATH
                        + "\\"
                        + str(self.unique_id)
                        + f" Ref EIS{string_to_add}.csv"
                    )
                    LOGGER.debug(f"Saving data to {filepath}")
                    df.to_csv(filepath)

                    # Break the loop
                    break_loop = True

            except Exception as e:
                LOGGER.error(f"Error in potentiostat measurement: {e}")
                LOGGER.info("Trying again in 120 seconds")
                time.sleep(120)

            counter += 1

    def cleaning(self, well_number: int, sleep_time: int = 0, use_acid: bool = True):
        """Clean the well

        Args:
            well_number (int): Number of the well to clean
            sleep_time (int, optional): Time in seconds to sleep with HCl. Defaults to 0.
            use_acid (bool, optional): Use acid to clean the well. Defaults to True.
        """
        # To avoid cable clutter, move openTron first to pipette tip rack
        self.openTron.moveToWell(
            strLabwareName=self.labware_pipette_tips,
            strWellName=pipette_tips["NH4OH"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=130,
            intSpeed=100,  # mm/s
        )

        # Go to flush tool rack
        self.openTron.moveToWell(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["Flush_tool"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=tool_x_offset["Flush_tool"],
            fltOffsetY=tool_y_offset["Flush_tool"],
            fltOffsetZ=50,
            intSpeed=50,  # mm/s
        )

        # Pick up flush tool
        self.openTron.pickUpTip(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["Flush_tool"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=tool_x_offset["Flush_tool"],
            fltOffsetY=tool_y_offset["Flush_tool"],
            fltOffsetZ=tool_z_offset["Flush_tool"],
        )

        # Go to well
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=-0.5,
            fltOffsetY=0,
            fltOffsetZ=0,
            intSpeed=50,  # mm/s
        )

        # Go a little deeper
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=-0.5,
            fltOffsetY=0,
            fltOffsetZ=-30,
            intSpeed=50,  # mm/s
        )

        # Drain to avoid overflow
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Flush_tool_Drain"], volume=1
        )  # ml to dispense

        # Go a little deeper
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=-0.5,
            fltOffsetY=0,
            fltOffsetZ=-40,
            intSpeed=50,  # mm/s
        )

        # Drain to avoid overflow
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Flush_tool_Drain"], volume=1
        )  # ml to dispense

        # Go a little deeper
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=-0.5,
            fltOffsetY=0,
            fltOffsetZ=-50,
            intSpeed=50,  # mm/s
        )
        # Drain to avoid overflow
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Flush_tool_Drain"], volume=1
        )  # ml to dispense

        # Go to deepest position
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=-0.5,
            fltOffsetY=0,
            fltOffsetZ=-53.8,
            intSpeed=50,  # mm/s
        )

        # Drain
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Flush_tool_Drain"], volume=1
        )
        self.chemical_volumes_left["Waste"] -= self.well_volume

        # Flush with water
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Flush_tool_H2O"], volume=0.5
        )  # ml to dispense
        self.chemical_volumes_left["Flush_tool_H2O"] -= 0.5
        self.arduino.set_ultrasound_on(1, 5)
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Flush_tool_Drain"], volume=2
        )  # ml to dispense DRAIN
        self.chemical_volumes_left["Waste"] -= 0.5
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Flush_tool_H2O"], volume=0.5
        )  # ml to dispense
        self.chemical_volumes_left["Flush_tool_H2O"] -= 0.5
        self.arduino.set_ultrasound_on(1, 5)
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Flush_tool_Drain"], volume=2
        )  # ml to dispense DRAIN
        self.chemical_volumes_left["Waste"] -= 0.5

        # Save the volumes of the chemicals left
        self.save_chemical_volumes_left()

        if use_acid is True:
            # Flush with acid
            self.arduino.dispense_ml(
                pump=peristaltic_pump_content["Flush_tool_HCl"], volume=0.5
            )  # ml to dispense
            self.chemical_volumes_left["Flush_tool_HCl"] -= 0.5
            LOGGER.info(f"Sleeping for {sleep_time} seconds")
            time.sleep(sleep_time)  # Sleep to let the acid work
            self.arduino.set_ultrasound_on(1, 5)
            self.arduino.dispense_ml(
                pump=peristaltic_pump_content["Flush_tool_Drain"], volume=2
            )  # ml to dispense DRAIN
            self.chemical_volumes_left["Waste"] -= 0.5

            # Flush with water
            self.arduino.dispense_ml(
                pump=peristaltic_pump_content["Flush_tool_H2O"], volume=0.5
            )  # ml to dispense
            self.chemical_volumes_left["Flush_tool_H2O"] -= 0.5
            self.arduino.set_ultrasound_on(1, 5)
            self.arduino.dispense_ml(
                pump=peristaltic_pump_content["Flush_tool_Drain"], volume=2
            )  # ml to dispense DRAIN
            self.chemical_volumes_left["Waste"] -= 0.5
            self.arduino.dispense_ml(
                pump=peristaltic_pump_content["Flush_tool_H2O"], volume=0.5
            )  # ml to dispense
            self.chemical_volumes_left["Flush_tool_H2O"] -= 0.5
            self.arduino.set_ultrasound_on(1, 5)
            self.arduino.dispense_ml(
                pump=peristaltic_pump_content["Flush_tool_Drain"], volume=2
            )  # ml to dispense DRAIN
            self.chemical_volumes_left["Waste"] -= 0.5

            # Save the volumes of the chemicals left
            self.save_chemical_volumes_left()

        # Go straight up in the air
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=-0.5,
            fltOffsetY=0,
            fltOffsetZ=20,
            intSpeed=50,  # mm/s
        )

        # Go to tool rack
        self.openTron.moveToWell(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["Flush_tool"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=tool_x_offset["Flush_tool"],
            fltOffsetY=tool_y_offset["Flush_tool"],
            fltOffsetZ=50,
            intSpeed=50,  # mm/s
        )

        # Drop tip
        self.openTron.dropTip(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["Flush_tool"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="bottom",
            fltOffsetX=tool_x_offset["Flush_tool"],
            fltOffsetY=tool_y_offset["Flush_tool"],
            fltOffsetZ=tool_z_dropoff["Flush_tool"],
            boolHomeAfter=False,
            boolAlternateDropLocation=False,
        )

        # Go stright up in the air
        self.openTron.moveToWell(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["Flush_tool"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=tool_x_offset["Flush_tool"],
            fltOffsetY=tool_y_offset["Flush_tool"],
            fltOffsetZ=100,
            intSpeed=50,  # mm/s
        )

    def normalize_volume(self, chemicals_to_mix: dict):
        # normalize the volume of each chemical dividing each volumes in the dict chemicals_to_mix with the sum of volumes in the dict so that the normalized sum  = 1
        sum_volume = sum(chemicals_to_mix.values())
        chemicals_to_mix = {k: v / sum_volume for k, v in chemicals_to_mix.items()}
        return chemicals_to_mix

    def dose_chemicals(
        self, chemicals_to_mix: dict, well_number: int, total_volume: float
    ):
        """Mix chemicals in a well

        Args:
            chemicals_to_mix (dict): Form must be: {"chemical_name": % of total volume}
            well_number (int): Well number to mix chemicals in
            total_volume (float): Total volume in ml
        """
        total_volume = int(total_volume * 1000)  # Convert to uL

        # Normalize the volume of each chemical
        chemicals_to_mix = self.normalize_volume(chemicals_to_mix)

        # Loop through all chemicals to mix
        for chemical, percentage in chemicals_to_mix.items():
            if percentage == 0:
                continue
            volume_to_dispense = int(percentage * total_volume)

            LOGGER.info(
                f"Mixing {chemical} with {percentage*total_volume} uL to well {wells[well_number]}"
            )
            # Move to pipette rack
            self.openTron.moveToWell(
                strLabwareName=self.labware_pipette_tips,
                strWellName=pipette_tips[chemical],
                strPipetteName=self.openTron_pipette_name,
                strOffsetStart="top",
                fltOffsetX=0,
                fltOffsetY=0,
                fltOffsetZ=50,
            )
            # Pick up tip
            self.openTron.pickUpTip(
                strLabwareName=self.labware_pipette_tips,
                strWellName=pipette_tips[chemical],
                strPipetteName=self.openTron_pipette_name,
                strOffsetStart="top",
                fltOffsetX=0,
                fltOffsetY=0,
                fltOffsetZ=0,
            )

            volume_left = volume_to_dispense
            for dispense in range(0, volume_to_dispense, 1000):
                if volume_left < 1000:
                    dispense_volume = volume_left
                else:
                    dispense_volume = 1000

                LOGGER.info(f"Aspirating {dispense_volume} uL of {chemical}")
                # Move to stock solution
                self.openTron.moveToWell(
                    strLabwareName=pipetteable_chemical_racks[chemical],
                    strWellName=pipetteable_chemicals[chemical],
                    strPipetteName=self.openTron_pipette_name,
                    strOffsetStart="top",
                    fltOffsetX=0,
                    fltOffsetY=0,
                    fltOffsetZ=0,
                )
                # Aspirate
                self.openTron.aspirate(
                    strLabwareName=pipetteable_chemical_racks[chemical],
                    strWellName=pipetteable_chemicals[chemical],
                    strPipetteName=self.openTron_pipette_name,
                    intVolume=dispense_volume,  # uL
                    strOffsetStart="top",
                    fltOffsetX=0,
                    fltOffsetY=0,
                    fltOffsetZ=-50,
                )
                # Go straight up in the air
                self.openTron.moveToWell(
                    strLabwareName=pipetteable_chemical_racks[chemical],
                    strWellName=pipetteable_chemicals[chemical],
                    strPipetteName=self.openTron_pipette_name,
                    strOffsetStart="top",
                    fltOffsetX=0,
                    fltOffsetY=0,
                    fltOffsetZ=80,
                )
                # Go to well
                self.openTron.moveToWell(
                    strLabwareName=self.labware_well_plate,
                    strWellName=wells[well_number],
                    strPipetteName=self.openTron_pipette_name,
                    strOffsetStart="top",
                    fltOffsetX=0,
                    fltOffsetY=0,
                    fltOffsetZ=10,
                )
                LOGGER.info(f"Dispensing {dispense_volume} uL of {chemical}")
                # Dispense
                self.openTron.dispense(
                    strLabwareName=self.labware_well_plate,
                    strWellName=wells[well_number],
                    strPipetteName=self.openTron_pipette_name,
                    intVolume=dispense_volume,  # uL
                    strOffsetStart="top",
                    fltOffsetX=0,
                    fltOffsetY=0,
                    fltOffsetZ=0,
                    fltFlowRate=100,
                )
                volume_left -= dispense_volume

                # Update the volume of the chemical left
                self.chemical_volumes_left[chemical] -= dispense_volume

                # Save the volumes of the chemicals left
                self.save_chemical_volumes_left()

            # Go to pipette tip rack
            self.openTron.moveToWell(
                strLabwareName=self.labware_pipette_tips,
                strWellName=pipette_tips[chemical],
                strPipetteName=self.openTron_pipette_name,
                strOffsetStart="top",
                fltOffsetX=0,
                fltOffsetY=0,
                fltOffsetZ=20,
            )
            LOGGER.info(f"Dropping tip for {chemical}")
            # Drop tip
            self.openTron.dropTip(
                strLabwareName=self.labware_pipette_tips,
                strWellName=pipette_tips[chemical],
                strPipetteName=self.openTron_pipette_name,
                strOffsetStart="bottom",
                fltOffsetX=0,
                fltOffsetY=0,
                fltOffsetZ=10,
                boolHomeAfter=False,
                boolAlternateDropLocation=False,
            )

    def perform_electrodeposition(
        self, well_number: int, electrodeposition_time: float = 10
    ):
        """Perform electrodeposition of the sample

        Args:
            well_number (int): Well number to perform electrodeposition in
            seconds (float, optional): Duration of the electrodeposition in seconds. Defaults to 10.
        """
        # Go to Ni deposition tool
        self.openTron.moveToWell(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["Ni_electrode"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=50,
        )
        # Pick up Ni deposition tool
        self.openTron.pickUpTip(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["Ni_electrode"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=tool_x_offset["Ni_electrode"],
            fltOffsetY=tool_y_offset["Ni_electrode"],
            fltOffsetZ=tool_z_offset["Ni_electrode"],
        )
        # Go to well at slow speed due to cable clutter
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=1,
            fltOffsetZ=0,
            intSpeed=50,  # mm/s
        )
        # Go down in the well
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=1,
            fltOffsetZ=-15,
            intSpeed=50,  # mm/s
        )

        # Switch relay on to make reference electrode the nickel deposition electrode
        self.arduino.set_relay_on(8)

        # Perform the actual electrochemical deposition
        self.perform_potentiostat_electrodeposition(seconds=electrodeposition_time)

        # Switch relay off to make reference electrode the real reference electrode
        self.arduino.set_relay_off(8)

        # Go straight up from the well
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=1,
            fltOffsetZ=20,
            intSpeed=50,  # mm/s
        )

        # Go to cleaning cartridge
        self.openTron.moveToWell(
            strLabwareName=self.labware_cleaning_cartridge,
            strWellName="A2",
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=-33,
            intSpeed=50,  # mm/s
        )

        # Flush the electrode in the cleaning station/cartridge
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_H2O"],
            volume=self.cleaning_station_volume,
        )
        self.chemical_volumes_left["Cartridge_H2O"] -= self.cleaning_station_volume
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_Drain"],
            volume=self.cleaning_station_volume + 1,
        )
        self.chemical_volumes_left["Waste"] -= self.cleaning_station_volume
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_HCl"],
            volume=self.cleaning_station_volume,
        )
        self.chemical_volumes_left["Cartridge_HCl"] -= self.cleaning_station_volume
        self.arduino.set_ultrasound_on(0, 15)
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_Drain"],
            volume=self.cleaning_station_volume + 1,
        )
        self.chemical_volumes_left["Waste"] -= self.cleaning_station_volume
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_H2O"],
            volume=self.cleaning_station_volume,
        )
        self.chemical_volumes_left["Cartridge_H2O"] -= self.cleaning_station_volume
        self.arduino.set_ultrasound_on(0, 5)
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_Drain"],
            volume=self.cleaning_station_volume + 1,
        )
        self.chemical_volumes_left["Waste"] -= self.cleaning_station_volume

        # Save the volumes of the chemicals left
        self.save_chemical_volumes_left()

        # Move straight up
        self.openTron.moveToWell(
            strLabwareName=self.labware_cleaning_cartridge,
            strWellName="A2",
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=20,
            intSpeed=50,  # mm/s
        )
        # Go to tool rack Ni deposition tool
        self.openTron.moveToWell(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["Ni_electrode"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=tool_x_offset["Ni_electrode"],
            fltOffsetY=tool_y_offset["Ni_electrode"],
            fltOffsetZ=20,
            intSpeed=50,  # mm/s
        )
        # Drop Ni deposition tool
        self.openTron.dropTip(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["Ni_electrode"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="bottom",
            fltOffsetX=tool_x_offset["Ni_electrode"],
            fltOffsetY=tool_y_offset["Ni_electrode"],
            fltOffsetZ=tool_z_dropoff["Ni_electrode"],
            boolHomeAfter=False,
            boolAlternateDropLocation=False,
        )

    def dispense_electrolyte(self, volume: float, chemical: str, well_number: int):
        volume = volume * 1000

        # Pipette 80% of the volume of KOH into the well
        self.openTron.moveToWell(
            strLabwareName=self.labware_pipette_tips,
            strWellName=pipette_tips[chemical],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=20,
        )
        # Pick up tip
        self.openTron.pickUpTip(
            strLabwareName=self.labware_pipette_tips,
            strWellName=pipette_tips[chemical],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=0,
        )
        volume_left = volume
        for dispense in range(0, volume, 1000):
            if volume_left < 1000:
                dispense_volume = volume_left
            else:
                dispense_volume = 1000

            # Move to stock solution
            self.openTron.moveToWell(
                strLabwareName=pipetteable_chemical_racks[chemical],
                strWellName=pipetteable_chemicals[chemical],
                strPipetteName=self.openTron_pipette_name,
                strOffsetStart="top",
                fltOffsetX=0,
                fltOffsetY=0,
                fltOffsetZ=0,
            )

            # Aspirate
            self.openTron.aspirate(
                strLabwareName=pipetteable_chemical_racks[chemical],
                strWellName=pipetteable_chemicals[chemical],
                strPipetteName=self.openTron_pipette_name,
                intVolume=dispense_volume,  # uL
                strOffsetStart="top",
                fltOffsetX=0,
                fltOffsetY=0,
                fltOffsetZ=-50,
            )
            # Go to well
            self.openTron.moveToWell(
                strLabwareName=self.labware_well_plate,
                strWellName=wells[well_number],
                strPipetteName=self.openTron_pipette_name,
                strOffsetStart="top",
                fltOffsetX=0,
                fltOffsetY=0,
                fltOffsetZ=10,
            )
            # Go down in well
            self.openTron.moveToWell(
                strLabwareName=self.labware_well_plate,
                strWellName=wells[well_number],
                strPipetteName=self.openTron_pipette_name,
                strOffsetStart="top",
                fltOffsetX=0,
                fltOffsetY=0,
                fltOffsetZ=-10,
            )
            # Dispense
            self.openTron.dispense(
                strLabwareName=self.labware_well_plate,
                strWellName=wells[well_number],
                strPipetteName=self.openTron_pipette_name,
                intVolume=dispense_volume,  # uL
                strOffsetStart="top",
                fltOffsetX=0,
                fltOffsetY=0,
                fltOffsetZ=-10,
            )
            volume_left -= dispense_volume

            # Update chemical volumes left
            self.chemical_volumes_left[chemical] -= dispense_volume

            # Save the volumes left to file
            self.save_chemical_volumes_left()

            # Go up from well
            self.openTron.moveToWell(
                strLabwareName=self.labware_well_plate,
                strWellName=wells[well_number],
                strPipetteName=self.openTron_pipette_name,
                strOffsetStart="top",
                fltOffsetX=0,
                fltOffsetY=0,
                fltOffsetZ=10,
            )

        # Go to pipette tip rack
        self.openTron.moveToWell(
            strLabwareName=self.labware_pipette_tips,
            strWellName=pipette_tips[chemical],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=20,
        )
        # Drop tip
        self.openTron.dropTip(
            strLabwareName=self.labware_pipette_tips,
            strWellName=pipette_tips[chemical],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="bottom",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=10,
            boolHomeAfter=False,
            boolAlternateDropLocation=False,
        )

    def perform_electrochemical_testing(self, well_number: int):
        # Use the OER_electrode
        self.openTron.moveToWell(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["OER_electrode"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=tool_x_offset["OER_electrode"],
            fltOffsetY=tool_y_offset["OER_electrode"],
            fltOffsetZ=10,
        )
        self.openTron.pickUpTip(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["OER_electrode"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=tool_x_offset["OER_electrode"],
            fltOffsetY=tool_y_offset["OER_electrode"],
            fltOffsetZ=tool_z_offset["OER_electrode"],
        )

        # Set the variable to indicate that the electrode is on the pipette
        self.electrode_is_on_pipette = True

        # Go to well
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=10,
            intSpeed=50,  # mm/s
        )
        # Go down in well
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=-18,
            intSpeed=10,  # mm/s
        )

        # Get temperature of the well and store in metadata
        self.metadata.loc[
            0, "well_temperature_during_electrochemical_measurements [C]"
        ] = self.arduino.get_temperature1()
        self.save_metadata()

        # Perform reference electrode calibration
        self.perform_potentiostat_reference_measurement(" before")

        # Perform the actual electrochemical testing
        self.perform_potentiostat_measurements()

        # Perform reference electrode calibration
        self.perform_potentiostat_reference_measurement(" after")

        # Go straight up from the well
        self.openTron.moveToWell(
            strLabwareName=self.labware_well_plate,
            strWellName=wells[well_number],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=20,
            intSpeed=50,  # mm/s
        )
        # Go to cleaning cartridge
        self.openTron.moveToWell(
            strLabwareName=self.labware_cleaning_cartridge,
            strWellName="A2",
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=20,
            intSpeed=50,  # mm/s
        )
        # Go down in well
        self.openTron.moveToWell(
            strLabwareName=self.labware_cleaning_cartridge,
            strWellName="A2",
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=-33,
            intSpeed=10,  # mm/s
        )

        # Flush the electrode in the cleaning station/cartridge
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_H2O"],
            volume=self.cleaning_station_volume,
        )
        # Update chemical volumes left
        self.chemical_volumes_left["Cartridge_H2O"] -= self.cleaning_station_volume

        # Drain
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_Drain"],
            volume=self.cleaning_station_volume + 1,
        )
        # Update chemical volumes left
        self.chemical_volumes_left["Waste"] -= self.cleaning_station_volume

        # Flush with HCl
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_HCl"],
            volume=self.cleaning_station_volume,
        )
        self.chemical_volumes_left["Cartridge_HCl"] -= self.cleaning_station_volume
        self.arduino.set_ultrasound_on(0, 15)

        # Drain
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_Drain"],
            volume=self.cleaning_station_volume + 1,
        )
        # Update chemical volumes left
        self.chemical_volumes_left["Waste"] -= self.cleaning_station_volume

        # Flush with water
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_H2O"],
            volume=self.cleaning_station_volume,
        )
        # Update chemical volumes left
        self.chemical_volumes_left["Cartridge_H2O"] -= self.cleaning_station_volume
        self.arduino.set_ultrasound_on(0, 5)

        # Drain
        self.arduino.dispense_ml(
            pump=peristaltic_pump_content["Cartridge_Drain"],
            volume=self.cleaning_station_volume + 1,
        )
        # Update chemical volumes left
        self.chemical_volumes_left["Waste"] -= self.cleaning_station_volume

        # Save the volumes left to file
        self.save_chemical_volumes_left()

        # Go straight up
        self.openTron.moveToWell(
            strLabwareName=self.labware_cleaning_cartridge,
            strWellName="A2",
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=0,
            fltOffsetY=0,
            fltOffsetZ=20,
            intSpeed=50,  # mm/s
        )
        # Go to tool rack
        self.openTron.moveToWell(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["OER_electrode"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="top",
            fltOffsetX=tool_x_offset["OER_electrode"],
            fltOffsetY=tool_y_offset["OER_electrode"],
            fltOffsetZ=50,
            intSpeed=50,  # mm/s
        )
        # Drop OER electrode
        self.openTron.dropTip(
            strLabwareName=self.labware_tool_rack,
            strWellName=labware_tools["OER_electrode"],
            strPipetteName=self.openTron_pipette_name,
            strOffsetStart="bottom",
            fltOffsetX=tool_x_offset["OER_electrode"],
            fltOffsetY=tool_y_offset["OER_electrode"],
            fltOffsetZ=tool_z_dropoff["OER_electrode"],
            boolHomeAfter=False,
            boolAlternateDropLocation=False,
        )

        # Set the variable to indicate that the electrode is no more on the pipette
        self.electrode_is_on_pipette = False

    def find_ohmic_resistance(
        self, df: pd.DataFrame, column_name_imag: str, column_name_real
    ) -> float:
        """Find the ohmic resistance from the EIS data

        Args:
            data (pd.DataFrame): EIS data
            column_name_imag (str): Column name of the imaginary impedance
            column_name_real (str): Column name of the real impedance

        Returns:
            float: Ohmic resistance
        """
        # Select the first 10 rows of data dataframe to avoid a negative
        # tail of the ohmic resistance at higher frequencies
        df = df.iloc[:10]

        # Finding ohmic resistance
        LOGGER.info("Finding ohmic resistance")

        # If column_name_imag = 0 and column_name_real = 0 exist, delete this row
        df = df[(df[column_name_imag] != 0) & (df[column_name_real] != 0)]

        row_index = df[column_name_imag].abs().idxmin(skipna=True)
        if row_index is None:
            raise ValueError("EIS data does not contain valid impedance values.")
        LOGGER.debug(f"Row index of minimum imaginary impedance: {row_index}")
        LOGGER.debug(f"Imaginary impedance: {df.loc[row_index, column_name_imag]}")
        LOGGER.debug(f"Real impedance: {df.loc[row_index, column_name_real]}")
        ohmic_resistance = round(float(df.loc[row_index, column_name_real]), 3)
        LOGGER.info(f"Ohmic resistance: {ohmic_resistance}")
        return ohmic_resistance

    def __del__(self):
        if self.electrode_is_on_pipette is True:
            self.emergency_parking_of_electrode(well_number=self.well_number)

        # Home robot
        self.openTron.homeRobot()
        # Turn off light
        self.openTron.lights(False)

        # Save metadata
        self.save_metadata()

        self.arduino.disconnect()

    def load_well_number(self):
        # Load well number from last_processed_well.txt and update it to +1 (until 14). If the file doesn't exist, start with 0.
        try:
            with open("last_processed_well.txt", "r") as f:
                well_number = int(f.read())
            # Update well number
            well_number += 1
        except ValueError:
            well_number = 0
        except FileNotFoundError:
            well_number = 0

        if (
            well_number > 13
        ):  # XXX THIS HAS TO CHANGE WITH MORE CARTRIDGES AND IN parameters.py
            # Throw error if all wells are used
            raise ValueError(
                "All wells are used. Please clean the well plate and delete the file last_processed_well.txt."
            )

        # Update metadata
        self.metadata.loc[0, "well_number"] = well_number

        return well_number

    def save_well_number(self):
        """Save well number to last_processed_well.txt"""

        # Save well number to last_processed_well.txt
        with open("last_processed_well.txt", "w") as f:
            f.write(str(self.well_number))

    def save_metadata(self):
        """Save metadata

        Saves metadata to a csv file. If the file exists, it appends the metadata to the file. If the file doesn't exist, it creates the file.

        Args by class attribute:
            metadata (pd.DataFrame): Metadata to save
        """
        LOGGER.debug(f"Saving metadata \n {self.metadata}")
        # Save metadata to a csv file
        # if file exists, append to it (after checking if there is already a line with the same unique_id).
        # If there is already a line with the same unique_id, overwrite that line with the new data.
        # If file doesn't exist, create it.
        if os.path.isfile("metadata.csv"):
            df = pd.read_csv("metadata.csv")
            if self.metadata["unique_id"].values[0] in df["unique_id"].values:
                df = df[df["unique_id"] != self.metadata["unique_id"].values[0]]
                df = pd.concat([df, self.metadata])
                df.to_csv("metadata.csv", index=False)
            else:
                self.metadata.to_csv(
                    "metadata.csv", mode="a", header=False, index=False
                )
        else:
            self.metadata.to_csv("metadata.csv", index=False)

    def check_chemical_volumes(
        self,
        chemicals_to_mix: dict,
        dispense_ml_electrolyte: float,
        electrolyte: str = "KOH",
    ):
        """Check if the total volume of chemicals to mix, electrolyte and
        cleaning solution is less than the total volume of the well

        Args:
            chemicals_to_mix (dict): Form must be: {"chemical_name": volume}
            dispense_ml_electrolyte (float): Volume of electrolyte to dispense in ml
            electrolyte (str, optional): Electrolyte to dispense

        Raises:
            ValueError: If the total volume of chemicals to mix, electrolyte
            and cleaning solution is greater than the total volume of the well
            FileNotFoundError: If the file 'chemicals_left.txt' is not found
        """

        list_of_chemicals = [
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_HCl": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_HCl": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Cartridge_H2O": self.cleaning_station_volume},
            {"Waste": self.cleaning_station_volume},
            {"Cartridge_HCl": self.cleaning_station_volume},
            {"Waste": self.cleaning_station_volume},
            {"Cartridge_H2O": self.cleaning_station_volume},
            {"Waste": self.cleaning_station_volume},
            {electrolyte: dispense_ml_electrolyte},
            {"Waste": dispense_ml_electrolyte},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_HCl": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Flush_tool_H2O": 0.5},
            {"Waste": 0.5},
            {"Cartridge_H2O": self.cleaning_station_volume},
            {"Waste": self.cleaning_station_volume},
            {"Cartridge_HCl": self.cleaning_station_volume},
            {"Waste": self.cleaning_station_volume},
            {"Cartridge_H2O": self.cleaning_station_volume},
            {"Waste": self.cleaning_station_volume},
        ]

        # Add chemicals_to_mix to list_of_chemicals
        for chemical, volume in chemicals_to_mix.items():
            list_of_chemicals.append({chemical: volume*self.well_volume})

        # Add the waste amount corresponding to chemicals_to_mix
        # to list_of_chemicals as waste
        list_of_chemicals.append({"Waste": self.well_volume})

        # Trigger to flip a warning further down in the code
        trigger_stop = False

        # Load the dictionary of chemicals in stock solutions
        chemicals_left = self.chemical_volumes_left.copy()

        LOGGER.info(f"Chemicals left before experiment: {chemicals_left}")

        # Deduct each of the volumes listed in list_of_chemicals
        # from chemicals_left.
        for chemical in list_of_chemicals:
            for key, value in chemical.items():
                chemicals_left[key] -= value
                if chemicals_left[key] <= 0:
                    trigger_stop = True
                    LOGGER.warning(
                        f"{key} will run out of stock solution. Please refill the stock solution."
                    )
        LOGGER.info(f"Chemicals left after experiment: {chemicals_left}")

        if trigger_stop:
            # Throw exception if any of the chemicals
            # will run out of stock solution
            self.send_mail(
                "openTron: No more chemicals",
                "openTron missing stock solution",
                ["nis@dosan.dk"],
            )
            raise ValueError(
                "One or more chemicals will run out of stock solution. Please refill the stock solution."
            )
        else:
            LOGGER.info("All chemicals have enough stock solution.")

    def run_experiment(
        self,
        chemicals_to_mix: dict,
        dispense_ml_electrolyte: float,
        electrolyte: str = "KOH",
        well_number: int = None,
        electrodeposition_time: float = 10,
        electrodeposition_temperature: float = 0,
        chemical_ultrasound_mixing_time: int = 30,
        chemical_rest_time: int = 300,
    ):
        """Run the experiment

        Args:
            chemicals_to_mix (dict): Form must be: {"chemical_name": % of total volume}
            dispense_ml_electrolyte (float): Volume of electrolyte to dispense in ml
            electrolyte (str, optional): Electrolyte to dispense. Defaults to "KOH".
            well_number (int, optional): Well number to run the experiment in. Defaults to None.
            electrodeposition_time (float, optional): Duration of the electrodeposition in seconds. Defaults to 10.
            chemical_ultrasound_mixing_time (int, optional): Time to mix chemicals with ultrasound in seconds. Defaults to 30.
            electrodeposition_temperature (float, optional): Temperature of the electrodeposition in degrees Celsius. Defaults to 0.
            chemical_ultrasound_mixing_time (int, optional): Time to mix chemicals with ultrasound in seconds. Defaults to 30.
            chemical_rest_time (int, optional): Time to rest after mixing chemicals in seconds. Defaults to 300.
        """
        # Check that there is enough stock solution for a run
        self.check_chemical_volumes(
            chemicals_to_mix=chemicals_to_mix,
            dispense_ml_electrolyte=dispense_ml_electrolyte,
            electrolyte=electrolyte,
        )

        # Send an email stating that the job i starting
        if well_number is not None:
            self.well_number = well_number
            self.metadata.loc[0, "well_number"] = well_number

        message = f"""Starting experiment {self.unique_id} 
        in well {self.well_number}
        with chemicals {chemicals_to_mix}."""
        self.send_mail(message, "openTron experiment starting", ["nis@dosan.dk"])

        self.metadata.loc[0, "chemicals_to_mix"] = str(chemicals_to_mix)
        self.metadata.loc[0, "total_volume [ml]"] = self.well_volume
        self.metadata.loc[0, "electrodeposition_time [s]"] = electrodeposition_time
        self.metadata.loc[0, "deposition_current [A]"] = self.deposition_current
        self.metadata.loc[0, "sample_surface_area [cm2]"] = self.sample_surface_area
        self.metadata.loc[0, "electrodeposition_temperature_setpoint [C]"] = (
            electrodeposition_temperature
        )
        self.metadata.loc[0, "cleaning_station_volume [ml]"] = (
            self.cleaning_station_volume
        )
        self.metadata.loc[0, "chemical_ultrasound_mixing_time [s]"] = (
            chemical_ultrasound_mixing_time
        )
        self.metadata.loc[0, "chemical_rest_time [s]"] = chemical_rest_time
        self.save_metadata()
        self.save_well_number()

        LOGGER.info(f"Starting experiment {self.unique_id} in well {self.well_number}")
        LOGGER.info(f"Chemicals to mix: {chemicals_to_mix}")
        LOGGER.info(f"Electrolyte: {electrolyte} {dispense_ml_electrolyte} ml")
        LOGGER.info(f"Well volume: {self.well_volume} ml")
        LOGGER.info(f"Electrodeposition time: {electrodeposition_time} seconds")
        LOGGER.info(f"Cleaning cartridge volume: {self.cleaning_station_volume} ml")

        # Set temperature of the two heating plates
        self.arduino.set_temperature(0, 0)
        self.arduino.set_temperature(1, electrodeposition_temperature)

        # Home robot and turn on light
        self.openTron.lights(True)
        self.openTron.homeRobot()

        # Clean the well
        self.cleaning(well_number=self.well_number, sleep_time=30)

        # Dose chemicals
        self.dose_chemicals(
            chemicals_to_mix=chemicals_to_mix,
            well_number=self.well_number,
            total_volume=self.well_volume,
        )

        # Stirring of dispensed chemicals
        LOGGER.info(
            f"Stirring chemicals for {chemical_ultrasound_mixing_time} seconds."
        )
        self.arduino.set_ultrasound_on(1, chemical_ultrasound_mixing_time)
        LOGGER.info(
            f"Sleeping for {chemical_rest_time} seconds to let chemistry settle in."
        )
        time.sleep(chemical_rest_time)

        # Connect to admiral potentiostat
        self.initiate_potentiostat_admiral()

        # Run recipe for electrodeposition
        self.perform_electrodeposition(
            well_number=self.well_number, electrodeposition_time=electrodeposition_time
        )

        # Clean the well
        self.cleaning(well_number=self.well_number, sleep_time=0.1)

        # Dispense electrolyte
        self.dispense_electrolyte(
            volume=dispense_ml_electrolyte,
            chemical=electrolyte,
            well_number=self.well_number,
        )

        # Make sure the relay is off to make contact with the reference electrode
        self.arduino.set_relay_off(8)

        # Perform electrochemical testing
        self.perform_electrochemical_testing(well_number=self.well_number)

        # Disconnect admiral potentiostat
        self.close_potentiostat_admiral()

        # Clean the well
        self.cleaning(well_number=self.well_number, sleep_time=0, use_acid=False)

        # Set timestamp_end of metadata
        self.metadata.loc[0, "timestamp_end"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        # Set status of metadata
        self.metadata.loc[0, "status_of_run"] = "success"

        # Set temperature to 0 C so it doesnt heat
        self.arduino.set_temperature(0, 0)
        self.arduino.set_temperature(1, 0)

        # Save metadata
        self.save_metadata()

        # Send an email stating that the job i done
        message = f"""Finished experiment {self.unique_id} with success.
        Overpotential is {self.metadata.loc[0, 'corrected_potential_at_10mAcm2 [V]']} V.
        """
        self.send_mail(message, "openTron experiment ended", ["nis@dosan.dk"])

        return self.metadata.loc[0, "corrected_potential_at_10mAcm2 [V]"]
