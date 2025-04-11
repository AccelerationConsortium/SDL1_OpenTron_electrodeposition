# SDL1_OpenTron_electrodeposition
This is the repository for the work done by external PhD researcher, Nis Fisker-Bødker from the Danish Technical University (DTU), while working at University of Toronto for the Acceleration Consortium.
The software combines the use of an opentron OT2 and a Sparkfun Arduino Uno to produce a facility for AI optimised electrodeposition of Oxygen Evolution Reaction (OER) catalyst for watersplitting in alkaline environment.

Please pay attention: Due to the Admiral Squidstat software, this will only work on a Windows X86_64 platform and not on Mac/Linux.

# 3D print and machine components
All files used for 3D printing, cutting and ordering at www.hubs.com can be found in /3D_files/. Consider to read the journal article "Democratizing self-driving lab platform for electrodeposition of catalyst and electrochemical validation" to understand the content.

# Installation of Python environment
Install miniconda on your computer. Create an invironment for your opentron:
````
conda create -n opentron python=3
conda activate opentron
````
# Install Arduino IDE and test the connection to your Arduino
Refer to Arduino documentation for this step.
Remember to set the right address for the temperature sensors and the quad relays as found in the firmware in src/arduino/main.ino
Cable everything as according to the schematics in the journal aticle "Democratizing self-driving lab platform for electrodeposition of catalyst and electrochemical validation" and in the folder /manuals/Electric_diagram.pdf.
A bill of materials can be found in /manuals/Canada Electrodeposition Bill of Materials (BOM).xlsx

Once the firmware from src/arduino/ has been uploaded to the Arduino, add a 10 micro farad capacitor between RESET and GND to avoid the PID regulation to reset itself all the time on the board.

# 1: Install requirement: Admiral Squidstat Plus potentiostat
On a Windows X86_64/AMD64 machine install the Admiral Instrument Squidstat software. Afterwards download the Wheel file from here:
https://github.com/Admiral-Instruments/AdmiralSquidstatAPI/tree/main/SquidstatLibrary/windows/pythonWrapper/Release

There is already a working Squidstat Library in this repository which can be used. It is however not updated.
In a terminal within the right python environment and folder, run the command (adjust to your version):
````
pip install SquidstatPyLibrary-1.8.0.5-py3-none-win_amd64.whl
````
# 2: Install requirement: opentron OT2 python wrapper
In a terminal with the correct python environment and folder run:
````
git clone https://github.com/dpersaud/opentronsHTTPAPI_wrapper.git
cd opentronsHTTPAPI_wrapper
pip install -e .
````

# 3: Install the SDL1_OpenTron_electrodeposition experiment
This is what is contained in this particular git-repo.

In a terminal with the correct python environment run:
````
git clone https://github.com/AccelerationConsortium/SDL1_OpenTron_electrodeposition.git
cd SDL1_OpenTron_electrodeposition
pip install -e .
````

# 4: Run the experiment
Run the experiment from the root of SDL1_OpenTron_electrodeposition/ by executing in an terminal:
````
python /src/python/main.py
````

# 5: Individual examples
Individual examples can be found in src/python/ where there are some simple files testing the functionality of the openTron, Arduino, Admiral potentiostat. For any debugging start with these simple examples.

# Plotting of data via plot.py
To export and plot the data from the Admiral and Biologic potentiostats run the src/python/plot.py file.

# parameters.py
It is very important to adjust /src/python/parameters.py to your setup. In here the positions on the openTron deck is defined as well as the chemicals, which relay on the arduino the chemical is attached etc. Spend a decent amount of time to familiarize yourself with the content.
In the future this should be integrated to a general robot_config.json

# experiment.py
This is basically the experiment. In the end of the class there is a method named run_experiment() which is basically the recipe of the experiment. Change it according to your needs.

# chemicals_left.txt
First of all sorry: This is a quick workaround to keep track of how much is in the bottles and vials on the setup. The experiment.py checks that it won't run dry by simple volume subtraction.
When refilling chemicals on the setup you must ensure that you also update this file acordingly with the new volumes.
In the future this should be integrated to a general robot_config.json

# last_processed_well.txt
Again sorry: This is a quick workaround to store the last processed well. Usually the openTron notation is eg. A1, A2, etc. but in this case it is from 0-14 with the 15 hole well I've used. Hole 14 is by the way occupied by a temperature sensor, so in reality you can only run from 0-13 wells.
The main reason it was used as a 0-14 number is because it was easier to iterate over numbers. In the future this should be integrated to a general robot_config.json

# metadata.csv
This file basically contains a table of all the experiments, their chemical combination, temperature, timestamp, overpotential during OER reaction at 10 mA/cm2 etc.
I would argue it is a good idea to keep something easy readable and comparable data like this in a single file.

# uid_run_number.txt
Every run has a unique ID which is tracked through this file.
In the future this should be integrated to a general robot_config.json

# Suggestions to future work
* Data should be placed elsewhere.
* biologic_XXX.whl, SquidstatPyLibrary-XXX.whl, Admiral github and openTron wrapper github should all be integrated into a the pip installable setup in this repo.
* Move uid_run_number.txt, last_processed_well.txt, chemicals_left.txt, parameters.py into a robot_config.json file.
* Modify main.py to accept .json files with all the experiment variables. This file should then continuesly be populated with metadata about eg. how much was dispensed, in which order, time for each step, measurements etc. as the experiment progress.

