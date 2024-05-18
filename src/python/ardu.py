import logging
import time
import serial
import serial.tools.list_ports
import pandas as pd
from pathlib import Path

LOGGER = logging.getLogger(__name__)


class Arduino:
    """Class for the robot relate activities."""

    def __init__(self, arduino_search_string: str = "CH340"):
        self.SERIAL_PORT = self.define_arduino_port(arduino_search_string)
        self.BAUD_RATE = 115200
        self.CONNECTION_TIMEOUT = 30  # seconds
        self.connect()

    def connect(
        self,
    ) -> None:
        """Connects to serial port of arduino"""
        # Connection to arduino
        self.connection = serial.Serial(
            port=self.SERIAL_PORT,
            baudrate=self.BAUD_RATE,
            timeout=self.CONNECTION_TIMEOUT,
        )
        time.sleep(2)  # initialization loadtime needs to be > 2 seconds

    def get_temperature0(self) -> float:
        """Measure the temeprature of the temperature sensor 0

        Returns:
            float: The measured temperature of the system in degree celsius.
        """
        LOGGER.info("Reading sample temperature sensor 0")
        self.connection.write("<read_temp0>".encode())
        temperature = self._read_temperature()
        return temperature

    def get_temperature0_ambient(self) -> float:
        """Measure the ambient temperature of the temperature sensor 0

        Returns:
            float: The measured temperature of the system in degree celsius.
        """

        LOGGER.info("Reading ambient temperature sensor 0")
        self.connection.write("<read_temp0_ambient>".encode())
        temperature = self._read_temperature()
        return temperature

    def get_temperature1(self) -> float:
        """Measure the temeprature of the temperature sensor 1

        Returns:
            float: The measured temperature of the system in degree celsius.
        """

        LOGGER.info("Reading sample temperature sensor 1")
        self.connection.write("<read_temp1>".encode())
        temperature = self._read_temperature()
        return temperature

    def get_temperature1_ambient(self) -> float:
        """Measure the ambient temperature of the temperature sensor 1

        Returns:
            float: The measured temperature of the system in degree celsius.
        """

        LOGGER.info("Reading ambient temperature sensor 1")
        self.connection.write("<read_temp1_ambient>".encode())
        temperature = self._read_temperature()
        return temperature

    def _read_temperature(self):
        """Read the temperature from the arduino.

        Returns:
            float: The measured temperature of the system in degree celsius.
        """

        received_response = False
        while received_response is False:
            try:
                temperature = self.connection.readline().decode()
                LOGGER.debug(f"Returned raw temperature: {temperature}")
                temperature = float(temperature)
                received_response = True
            except Exception:
                LOGGER.info("Waiting for arduino to respond")
                time.sleep(1)

        LOGGER.info(f"Temperature sensor: {temperature} C")
        return temperature

    def set_temperature(self, temp: float) -> None:
        """Set the temperature setpoint for PID controller.

        Args:
            temp (float): Temperature of the liquid to be measured.
        """
        temp = round(temp, 1)  # PID only take temperature upto 1 decimal place.
        # The input for PID controllers should be rid of decimals.
        # However the last digit is read as a decimal point.
        temp_pid = temp * 10

        self.conn_pid.write(f"<set_temp,{temp_pid}>".encode())
        self.conn_pid.readline().decode()
        LOGGER.info(f"Set temperature to {temp} C")
        time.sleep(2)

    def ultrasound(self, time_on: float):
        """Turns on the ultrasound for the given time.

        Args:
            time (float): Time in seconds which ultrasound should turned on.
        """
        time_ms = time_on * 1000  # arduino take time in milli seconds
        self.connection.write(f"<Ultrasound,{time_ms}>".encode())
        self.wait_for_arduino()

    def drain_cell(self, drain_time: float):
        """Turns on the drain pump for the given time.

        Args:
            time (float): Time in seconds which drain pump should turned on.
        """
        LOGGER.info(f"Draining cell for {drain_time} seconds")
        time_ms = drain_time * 1000  # arduino take time in milli seconds
        self.connection.write(f"<Drain,{time_ms}>".encode())
        self.wait_for_arduino()
        LOGGER.info("Draining completed")

    def transfer_liquid(self, transfer_time: float):
        """Turns on the transfer pump for the given time.

        Args:
            time (float): Time in seconds which drain pump should turned on.
        """
        LOGGER.info(f"Transfering liquid to cell for {transfer_time} seconds")
        time_ms = transfer_time * 1000  # arduino take time in milli seconds
        self.connection.write(f"<transfer,{time_ms}>".encode())
        self.wait_for_arduino()
        LOGGER.info("transfer liquid completed")

    def wait_for_arduino(self, max_wait_time: int = 2000):
        """To make sure arduino completed the particular task.

        Args:
            max_wait_time (int, optional): Maximum wait time to get response
            from arduino in seconds. Defaults to 2000.

        Raises:
            RuntimeWarning: Arduino did not finish the job in given time.
        """
        max_try = (1 / self.CONNECTION_TIMEOUT) * max_wait_time
        count = 0
        while count < max_try:
            LOGGER.debug("waiting for arduino to finish the task")
            state = self.connection.read().decode()
            if state == "#":
                LOGGER.debug("Arduino finished the task")
                break
            count += 1
        else:
            raise RuntimeWarning(
                "Arduino did not finish the job.",
                "Check arduino IDE or increase the value of max_wait_time.",
            )

    def vol_syringe_to_csv(
        self,
        pump_num: int,
        vol: float,
        max_volume: float = 6.0,
        fname: str = "syringe_volume.csv",
    ):
        """Check whether there is sufficient amount of liquid in syringe and
            update remaining volume to csv file.

        Args:
            pump_num (int): Pump number
            vol (float): volume to be dispensed
            fname (str, optional): Name of the csv file. Defaults to "syringe_volume.csv".
        """

        pump_df = self.read_vol_file(fname)
        vol_old = pump_df.query(f"Pump=={pump_num}")["Volume"].values[0]
        vol_new = vol_old - vol
        if vol_new < 0:
            raise ValueError("Amount of liquid in pump is not suffcient.")
        if vol_new > max_volume:
            raise ValueError(
                "Requested amount of liquid is larger than syringe capacity."
            )

        indx = pump_df.index[pump_df["Pump"] == pump_num]
        pump_df["Volume"].iloc[indx] = vol_new
        pump_df.to_csv(fname, index=False)

    def read_vol_file(self, fname):
        """Read the file with volume of liquid in each pump and return the dataframe

        Args:
            fname (str, optional): File in which volumes are saved.

        Returns:
            dátaframe: dataframe with pump number and remaining liquid in each pump
        """
        vol_file = Path(fname)
        if vol_file.is_file():
            df = pd.read_csv(vol_file)
        else:
            pump_list = list(range(0, self.PUMP_COUNT))
            vol_list = [0] * self.PUMP_COUNT
            df = pd.DataFrame({"Pump": pump_list, "Volume": vol_list})
        return df

    def atm_sensor_readings(self):
        """Humidity, pressure and temperature readings from sensor

        Returns:
            humidity, pressure, temperature: Humidity, pressure and temperature readings from sensor
        """
        self.connection.write("<get_sensor_readings>".encode())
        humidity = self.connection.readline().decode()
        pressure = self.connection.readline().decode()
        temperature = self.connection.readline().decode()
        time.sleep(2)
        return humidity, pressure, temperature

    def write_dif_pid(self, value: float) -> None:
        """Write parameter to given address of the PID
        Args:
            value (float): Value to be written
        """

        # The input for PID controllers should be rid of decimals.
        # However the last digit is read as a decimal point.
        value = round(value, 1)
        LOGGER.info(f"Writing {value} to PID")
        value_pid = value * 10
        self.conn_pid.write(f"<write_param,{value_pid}>".encode())
        self.conn_pid.readline().decode()

    def get_temp_pb2(self) -> float:
        """Ream parameter from the PID

        Returns:
            float: Parameter value from PID
        """

        self.conn_pid.write("<read_pb2>".encode())
        try:
            temp_value_pid = float(self.conn_pid.readline().decode())
            temp_value = temp_value_pid / 10  # last digit from PID is decimal
        except Exception:
            LOGGER.info("Waiting for PID to respond")
            time.sleep(1)
            LOGGER.info(self.conn_pid.readline().decode())
            self.conn_pid.readline().decode()
            temp_value = 0
        time.sleep(1)
        LOGGER.info(f"Probe2 temperature: {temp_value}")
        return temp_value

    def wait_for_temp(self, target, temp_tol, max_wait_time=600):
        """Wait for the temperature to reach the target temperature

        Args: target (float): Target temperature in C
        temp_tol (float): Temperature tolerance in C
        max_wait_time (float): Maximum wait time in seconds. Defaulst to 600 seconds
        """
        LOGGER.info(f"Waiting for temperature to reach {target} C")
        self.get_temp_pb2()
        tmp_temp = self.get_temp_pb1()
        start = time.perf_counter()
        counter = 0
        chamber_count = 0
        while (target + temp_tol) < tmp_temp or (target - temp_tol) > tmp_temp:
            time.sleep(1)
            chamber_temp = self.get_temp_pb2()
            tmp_temp = self.get_temp_pb1()
            elapsed_time = time.perf_counter() - start
            self.temp_to_csv(target, elapsed_time, chamber_temp, tmp_temp)
            if counter > max_wait_time:
                # self.set_temperature(20)
                RuntimeError(
                    f"Temperature did not reach the target temperature in {max_wait_time} seconds"
                )
            if chamber_temp > target + 5 and chamber_count < 1 and tmp_temp < target:
                self.set_temperature(15)
                time.sleep(2)
                self.pid_off()
                chamber_count = chamber_count + 1
            counter = counter + 1
        duration = time.perf_counter() - start
        LOGGER.info(f"Temperature reached in {duration} seconds")

    def temp_to_csv(self, target, elapsed_time, chamber_temperature, cell_temperature):
        """Save temperature readings to csv file

        Args:
            target (float): Target temperature in C
            chamber_temperature (float): Chamber temperature in C
            cell_temperature (float): Cell temperature in C
            elapsed_time (float): Elapsed time in seconds
        """
        t = time.localtime()
        temperatures = pd.DataFrame(
            [
                [
                    time.strftime("%H:%M:%S", t),
                    elapsed_time,
                    target,
                    chamber_temperature,
                    cell_temperature,
                ]
            ],
        )
        temperatures.to_csv(
            "temperatures_cell_constant_probe2.csv", mode="a", header=False, index=False
        )

    def pid_on(self):
        """Turn on the PID controller"""
        self.conn_pid.write("<pid_on>".encode())
        self.conn_pid.readline().decode()

    def pid_off(self):
        """Turn off the PID controller"""
        self.conn_pid.write("<pid_off>".encode())
        r = self.conn_pid.readline().decode()
        LOGGER.info(r)

    def clean_cell(
        self, cleaning_pump: int, vol: float, syringe_max_volume: float = 6.0
    ):
        """Clean the test cell from the liquid speciifed by cleaning pump

        Args:
            cleaning_pump (int): pump which have the liquid
            vol (float): volume of the cleaning liquid
            syringe_max_volume (float, optional): Maximum volume of the syringe in ml.
            Defaults to 6 ml.
        """
        self.drain_cell(20)
        time.sleep(2)
        self.transfer_liquid(20)
        time.sleep(2)
        self.drain_cell(20)
        self.pump(
            cleaning_pump, vol, "dispense", 3, syringe_max_volume=syringe_max_volume
        )
        time.sleep(2)
        self.transfer_liquid(30)
        time.sleep(2)
        self.transfer_liquid(30)
        time.sleep(2)
        self.drain_cell(30)
        time.sleep(2)
        self.drain_cell(30)

    def set_temperature_peltier(self, temp: float) -> None:
        """Set the temperature setpoint for PID controller.

        Args:
            temp (float): Temperature of the liquid to be measured.
        """

        self.conn_pid.write(f"<set_temp,{temp}>".encode())

        # self.conn_pid.readline().decode()
        LOGGER.info(f"Set temperature to {temp} C")
        time.sleep(2)

    def get_temp_peltier(self) -> float:
        """Measure the temeprature of the probe 1

        Returns:
            float: The measured temperature of the system in degree celsius.
        """

        self.conn_pid.write("<get_temp>".encode())
        try:
            probe_temp_pid = self.conn_pid.readline().decode()
            probe_temp_pid = float(probe_temp_pid)
            LOGGER.info(f"Probe1 Temperature: {probe_temp_pid} C")
            time.sleep(1)
        except Exception:
            probe_temp_pid = 0  # TODO find smart way to convert to float
            time.sleep(1)
            LOGGER.info("Waiting for PID to respond")
        return probe_temp_pid

    def get_output_peltier(self) -> float:
        """Get the output from PID controller for the peltier.

        Returns:
            float: The MOSFET output in the scale of 255.
        """

        self.conn_pid.write("<get_output>".encode())
        try:
            pid_output = float(self.conn_pid.readline().decode())
        except Exception:
            LOGGER.info("Waiting for PID to respond")
            LOGGER.info(self.conn_pid.readline().decode())
            pid_output = self.conn_pid.readline().decode()
        time.sleep(1)
        LOGGER.info(f"Output from PID: {pid_output} ")
        return pid_output

    def get_setpoint(self) -> float:
        """Get the output from PID controller for the peltier.

        Returns:
            float: The MOSFET output in the scale of 255.
        """

        self.conn_pid.write("<get_setpoint>".encode())
        try:
            pid_output = float(self.conn_pid.readline().decode())
        except Exception:
            LOGGER.info("Waiting for PID to respond")
            LOGGER.info(self.conn_pid.readline().decode())
            pid_output = self.conn_pid.readline().decode()
        time.sleep(1)
        LOGGER.info(f"Setpoint from PID: {pid_output}C")
        return pid_output

    def peltier_off(self):
        """Turn off the PID controller"""
        self.conn_pid.write("<peltier_off>".encode())
        r = self.conn_pid.readline().decode()
        LOGGER.info(r)

    def mix_ionic_liquids(self, vol_dict: dict) -> None:
        """Mix the liquids based on the given volumes. Not that only dispense here.
        Use the mix_liquids function if you need aspiration as well.
          TODO : Make the wait time and speed userdefined

        Args:
            vol_dict (dict): Dictionary with keys as pump num and value as volumes.
        """
        for pump_num, volume in vol_dict.items():
            if volume != 0.0:
                # self.pump(pump_num, volume, "aspirate", 5)
                # time.sleep(30)
                self.pump(pump_num, volume, "dispense", 10)
        time.sleep(2)

    def mix_cleaning_ionic_liquids(self, vol_dict: dict) -> None:
        """Mix the liquids based on the half of the given volumes for cleaning.
          TODO : Volumes should be normalized based on user input

        Args:
            vol_dict (dict): Dictionary with keys as pump num and value as volumes.
        """
        for pump_num, volume in vol_dict.items():
            if volume != 0.0:
                # self.pump(pump_num, volume, "aspirate", 5)
                # time.sleep(30)
                self.pump(pump_num, volume / 2, "dispense", 10)
        time.sleep(2)

    def wait_for_temp_peltier(self, target, temp_tol, max_wait_time=900):
        """Wait for the temperature to reach the target temperature

        Args: target (float): Target temperature in C
        temp_tol (float): Temperature tolerance in C
        max_wait_time (float): Maximum wait time in seconds. Defaulst to 600 seconds
        """
        LOGGER.info(f"Waiting for temperature to reach {target} C")
        tmp_temp = self.get_temp_peltier()
        start = time.perf_counter()
        counter = 0
        while (target + temp_tol) < tmp_temp or (target - temp_tol) > tmp_temp:
            time.sleep(1)
            tmp_temp = self.get_temp_peltier()
            # elapsed_time = time.perf_counter() - start
            if counter > max_wait_time:
                # self.set_temperature(20)
                RuntimeError(
                    f"Temperature did not reach the target temperature in {max_wait_time} seconds"
                )
            counter = counter + 1
        duration = time.perf_counter() - start
        LOGGER.info(f"Temperature reached in {duration} seconds")

    def define_arduino_port(self, search_string: str) -> str:
        """Find the port of the Arduino.

        Args:
            search_string (str, optional): Name of the Arduino.

        Returns:
            str: Port of the Arduino.
        """

        # List Arduinos on computer
        ports = list(serial.tools.list_ports.comports())
        logging.info("List of USB ports:")
        for p in ports:
            logging.info(f"{p}")
        arduino_ports = [p.device for p in ports if search_string in p.description]
        if not arduino_ports:
            logging.error("No Arduino found")
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            logging.warning("Multiple Arduinos found - using the first")

        # Automatically find Arduino
        arduino = str(serial.Serial(arduino_ports[0]).port)
        logging.info(f"Arduino found on port: {arduino}")
        return arduino

    def set_relay_on_time(self, relay_num: int, time_on: float) -> None:
        """Turn on the relay for the given time.

        Args:
            relay_num (int): Number of the relay.
            time_on (float): Time in seconds which relay should turned on.
        """
        LOGGER.info(f"Switching relay {relay_num} on for {time_on} seconds")
        time_ms = round(time_on * 1000, 0)
        self.connection.write(f"<set_relay_on_time,{relay_num},{time_ms}>".encode())
        self.wait_for_arduino()

    # def set_relay_on(self, relay_num: int) -> None:
    #     """Set the relay on.

    #     Args:
    #         relay_num (int): Number of the relay.
    #     """
    #     LOGGER.info(f"Switching relay {relay_num} on")
    #     self.connection.write(f"<set_relay_{relay_num}_on>".encode())
    #     self.wait_for_arduino()
    #     LOGGER.debug(f"Switched relay {relay_num} on successfully")

    # def set_relay_off(self, relay_num: int) -> None:
    #     """Set the relay off.

    #     Args:
    #         relay_num (int): Number of the relay.
    #     """
    #     LOGGER.info(f"Switching relay {relay_num} off")
    #     self.connection.write(f"<set_relay_{relay_num}_off>".encode())
    #     self.wait_for_arduino()
    #     LOGGER.debug(f"Switched relay {relay_num} off successfully")

    def get_relay_status(self, relay_num: int) -> bool:
        """Get the status of the relay.

        Args:
            relay_num (int): Number of the relay.

        Returns:
            bool: Status of the relay.
        """

        LOGGER.info(f"Getting status of relay {relay_num}")
        self.connection.write(f"<get_relay_{relay_num}_state>".encode())
        status = self.connection.readline().decode()
        if status == "True":
            LOGGER.info(f"Status of relay {relay_num}: High / On")
        else:
            LOGGER.info(f"Status of relay {relay_num}: Low / Off")

        return status == "True"
