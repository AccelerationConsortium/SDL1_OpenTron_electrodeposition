# SDL1_OpenTron_electrodeposition
This is the repository for the work done by external PhD researcher, Nis Fisker-Bødker from the Danish Technical University (DTU), while working at University of Toronto for the Acceleration Consortium.
The software combines the use of an opentron OT2 and a Sparkfun Arduino Uno to produce a facility for AI optimised electrodeposition of Oxygen Evolution Reaction (OER) catalyst for watersplitting in alkaline environment.

Please pay attention: Due to the Admiral Squidstat software, this will only work on a Windows X86_64 platform and not on Mac/Linux.

# 3D print and machine components
All files used for 3D printing, cutting and ordering at www.hubs.com can be found in /3D_files/. Consider to read the journal article "Democratizing self-driving lab platform for electrodeposition of catalyst and electrochemical validation" to understand the content.

# 1: Installation of Python environment
Install miniconda on your computer. Create an invironment for your opentron:
````
conda create -n opentron python=3.11
conda activate opentron
````

# 2: Download and install the SDL1_OpenTron_electrodeposition experiment
This is what is contained in this particular git-repo.

In a terminal with the correct python environment run:
````
git clone https://github.com/AccelerationConsortium/SDL1_OpenTron_electrodeposition.git
cd SDL1_OpenTron_electrodeposition
pip install -e .
````

# 3: Install requirement: Admiral Squidstat Plus potentiostat
On a Windows X86_64/AMD64 machine install the Admiral Instrument Squidstat software from the .exe file provided by the vendor. Afterwards install the Squidstat wheel provided with this release (/src/SquidstatPyLibrary-1.8.0.5-py3-none-win_amd64.whl) or download the newest wheel file from here:
https://github.com/Admiral-Instruments/AdmiralSquidstatAPI/tree/main/SquidstatLibrary/windows/pythonWrapper/Release

In a terminal within the right python environment and folder, run the command (adjust to your version if you downloaded another version of the wheel file):
````
pip install src/SquidstatPyLibrary-1.8.0.5-py3-none-win_amd64.whl
````

# 4: Install Arduino IDE and test the connection to your Arduino
Refer to Arduino documentation for this step and sparkfun.com for the additional components.
Set the right address for the temperature sensors and the quad relays as found in the firmware in src/arduino/main.ino. Here a summary as pseudocode is shown (don't try to use this directly in a .ino script):
````
// Quad relays
Relay_0-3 = 0x6D  // Default address
Relay_4-7 = 0x6C  // Modified address by programming

// Solid state relays for 110VAC/230VAC
Solid_state = 0x0A  // Default address

// Single relay 8
Relay_8 = 0x18  // Default address

// MCP9600 temperature sensor
tempSensor0 = 0x60  // Default address
tempSensor1 = 0x67  // Modified address by soldering on the PCB
````

Cable everything as according to the schematics in the journal article "AMPERE-2: An open-hardware, robotic platform for automated electrodeposition and electrochemical validation" and in the folder /manuals/Electric_diagram.pdf.
A bill of materials can be found in /manuals/Canada Electrodeposition Bill of Materials (BOM).xlsx

Once the firmware from /src/arduino/ has been uploaded to the Arduino, add a 10 micro farad capacitor between RESET and GND to avoid the PID regulation to reset itself all the time on the board.


# 4: Run the experiment
Examples are provided in /examples to both test the Admiral potentiostat, the Arduino, the opentron and the workflow with all machinary.

Run the experiment from the root of SDL1_OpenTron_electrodeposition/ by executing in an terminal:
````
python example/main.py
````

Please pay attention to the experiment.py. In case you are building your own experiment and workflow, this is the file you must edit to change the workflow of the robot, measurements etc.


# 5: Plotting of data via plot.py
Data (.csv and .jpeg plots) is placed in /data.
If you for some reason need to replot everything run the data/plot.py file.
````
python data/plot.py
````

# Important files
## parameters.py
It is very important to adjust /src/optenTron_electrodeposition/parameters.py to your setup. In here the positions on the openTron deck is defined as well as the chemicals, which relay on the arduino the chemical is attached etc. Spend a decent amount of time to familiarize yourself with the content.
In the future this should be integrated to a general robot_config.json
If you do change anything in parameters.py you must at the root of the SDL1_OpenTron_electrodeposition folder run the command again: 
````
pip install -e .
````

## experiment.py
This is basically the experiment. In the end of the class there is a method named run_experiment() which is basically the recipe of the experiment. Change it according to your needs.

## chemicals_left.txt
First of all sorry: This is a quick workaround to keep track of how much is in the bottles and vials on the setup. The experiment.py checks that it won't run dry by simple volume subtraction.
When refilling chemicals on the setup you must ensure that you also update this file acordingly with the new volumes.
In the future this should be integrated to a general robot_config.json

## last_processed_well.txt
Again sorry: This is a quick workaround to store the last processed well. Usually the openTron notation is eg. A1, A2, etc. but in this case it is from 0-14 with the 15 hole well I've used. Hole 14 is by the way occupied by a temperature sensor, so in reality you can only run from 0-13 wells.
The main reason it was used as a 0-14 number is because it was easier to iterate over numbers. In the future this should be integrated to a general robot_config.json

## metadata.csv
This file basically contains a table of all the experiments, their chemical combination, temperature, timestamp, overpotential during OER reaction at 10 mA/cm2 etc.
I would argue it is a good idea to keep something easy readable and comparable data like this in a single file.

## uid_run_number.txt
Every run has a unique ID which is tracked through this file.
In the future this should be integrated to a general robot_config.json

# Suggestions to future work
* Data should be placed elsewhere.
* SquidstatPyLibrary-XXX.whl should be replaced with an Admiral github and integrated into the pip installation of this repo.
* Move uid_run_number.txt, last_processed_well.txt, chemicals_left.txt, parameters.py into a robot_config.json file.
* Modify main.py to accept .json files with all the experiment variables. This file should then continuesly be populated with metadata about eg. how much was dispensed, in which order, time for each step, measurements etc. as the experiment progress.

