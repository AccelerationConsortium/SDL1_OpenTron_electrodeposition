from .ardu import Arduino
import logging
from datetime import datetime
import sys
import time
from admiral import AdmiralSquidstatWrapper
from .parameters import (
    list_of_pump_relays,
    list_of_ultrasonic_relays,
    pump_slope,
    pump_intercept,
    sample_surface_area,
    current_at_sample,
    volume_of_well,
    volume_of_pipette,
    peristaltic_pump_content,
)

# Folder where data and log-file will be saved
DATA_PATH = ""
NAME_OF_ARDUINO = "CH340"

# Surface area of sample in cm^2


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

# Initiate the arduino
robot = Arduino(
    arduino_search_string=NAME_OF_ARDUINO,  # Change string to match arduino name
    list_of_cartridges=[
        0,
        1,
    ],  # List of cartridges, where len(list) = number of cartridges
    list_of_pump_relays=list_of_pump_relays,
    list_of_ultrasonic_relays=list_of_ultrasonic_relays,
    pump_slope=pump_slope,
    pump_intercept=pump_intercept,
)

# Initialize the Admiral Squidstat Plus potentiostat
measurement = AdmiralSquidstatWrapper(port="COM5", instrument_name="Plus1894")


###############################################################################
# Workflow
###############################################################################
# Define the volumes to be pipetted
volumes = {
    "NH4OH": 1,
    "KCHO": 1,
    "KOH": 1,
    "Ni": 1,
    "Fe": 1,
    "Cr": 1,
    "Mn": 1,
    "Co": 1,
    "Zn": 1,
    "Cu": 1,
}
# Set temperature to 35 degrees for cartridge 0
robot.set_temperature(0, 25)
# Set temperature to 35 degrees for cartridge 1
robot.set_temperature(1, 35)

# Pick up flush tool
# Go to well

# Flush well with water
robot.dispense_ml(peristaltic_pump_content["Flush_tool_H2O"], 1.0)
# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 2.0)
# Flush well with HCl
robot.dispense_ml(peristaltic_pump_content["Flush_tool_HCl"], 1.0)

# Apply ultrasound for 30 seconds
robot.set_ultrasound_on(1, 30)
# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 2.0)
# Flush well with water
robot.dispense_ml(peristaltic_pump_content["Flush_tool_H2O"], 1.0)
# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 2.0)
# Flush well with water
robot.dispense_ml(peristaltic_pump_content["Flush_tool_H2O"], 1.0)
# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 2.0)

# Put back flush tool

# Pipette NH4OH into well
# Pipette KCHO into well
# Pipette Ni into well
# Pipette Fe into well
# Pipette Cr into well
# Pipette Mn into well
# Pipette Co into well
# Pipette Zn into well
# Pipette Cu into well

# Pick up Ni deposition tool

# Go to well and park with the tip dipped in the well

# Apply constant current for X seconds
measurement.setup_constant_current(
    holdAtCurrent=current_at_sample, samplingInterval=0.1, duration=10
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# Put back the Ni deposition tool

# Pick up the flush tool
# Go to well

# Flush well with water
robot.dispense_ml(peristaltic_pump_content["Flush_tool_H2O"], 1.0)
# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 2.0)
# Flush well with HCl
robot.dispense_ml(peristaltic_pump_content["Flush_tool_HCl"], 1.0)
# Apply ultrasound for 10 seconds
robot.set_ultrasound_on(1, 10)
# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 2.0)
# Flush well with water
robot.dispense_ml(peristaltic_pump_content["Flush_tool_H2O"], 1.0)
# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 2.0)
# Flush well with water
robot.dispense_ml(peristaltic_pump_content["Flush_tool_H2O"], 1.0)
# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 2.0)


# Put back the flush tool

# Pipette 80% of the volume of KOH into the well

# Pick up electrochemical testing electrode

###### Electrochemical testing
# 0 - Electrochemical Activation
measurement.setup_constant_current(
    holdAtCurrent=0.2 * sample_surface_area, samplingInterval=0.05, duration=60
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 1 - Perform CV
measurement.setup_cyclic_voltammetry(
    startVoltage=1.6,
    firstVoltageLimit=0.8,
    secondVoltageLimit=1.6,
    endVoltage=1.6,
    scanRate=0.2,
    samplingInterval=0.05,
    cycles=25,
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 2 - Perform CV
measurement.setup_cyclic_voltammetry(
    startVoltage=1.6,
    firstVoltageLimit=0.8,
    secondVoltageLimit=1.6,
    endVoltage=0.8,
    scanRate=0.01,
    samplingInterval=0.2,
    cycles=2,
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 3 - Perform EIS
measurement.setup_EIS_potentiostatic(
    start_frequency=500000,
    end_frequency=1,
    points_per_decade=10,
    voltage_bias=1.5,
    voltage_amplitude=0.01,
    number_of_runs=1,
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 4 - Perform CP at 100 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.1 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 5 - Perform CP at 50 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.05 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 6 - Perform CP at 20 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.02 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 7 - Perform CP at 10 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.01 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 8 - Perform CP at 5 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.005 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 9 - Perform CP at 2 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.002 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 10 - Perform CP at 1 mA/cm^2
measurement.setup_constant_current(
    holdAtCurrent=0.001 * sample_surface_area, samplingInterval=0.05, duration=70
)
measurement.run_experiment()
ac_data, dc_data = measurement.get_data()
measurement.clear_data()

# 11 - Perform CV
measurement.setup_cyclic_voltammetry(
    startVoltage=1.6,
    firstVoltageLimit=0.8,
    secondVoltageLimit=1.6,
    endVoltage=0.8,
    scanRate=0.01,
    samplingInterval=0.2,
    cycles=2,
)


# Save all data
# Plot all data
# Find potential at 10 mA/cm^2

# Put back the electrochemical testing electrode

# Pick up the flush tool
# Go to well

# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 4.0)
# Flush well with water
robot.dispense_ml(peristaltic_pump_content["Flush_tool_H2O"], 1.0)
# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 2.0)
# Flush well with water
robot.dispense_ml(peristaltic_pump_content["Flush_tool_H2O"], 1.0)
# Apply ultrasound
robot.set_ultrasound_on(1, 10)
# Drain well
robot.dispense_ml(peristaltic_pump_content["Flush_tool_Drain"], 2.0)

# Put back the flush tool

# Return potential at 10 mA/cm^2s
print("Done\n")
