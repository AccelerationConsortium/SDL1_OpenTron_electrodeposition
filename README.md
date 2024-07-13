# SDL1_OpenTron_electrodeposition
This is the repository for the work done by external PhD researcher, Nis Fisker-Bødker from the Danish Technical University (DTU).
The software combines the use of an openTron OT2 and a Sparkfun Arduino to produce a facility for AI optimised electrodeposition of Oxygen Evolution Reaction (OER) catalyst for watersplitting in alkaline environment.

Please pay attention: Due to the Admiral Squidstat software, this will only work on a Windows X86_64 platform and not on Mac/Linux.

# Installation of Pi Pico and Python environment
Install miniconda on your computer.
Create a mini python environment for the Pi Pico by opening a terminal and write:
````
conda create -n micropython python=3
conda activate micropython
pip install thonny
````
Now press the BOOTSEL button at the Pi Pico while you connect the USB cable to the computer.
Release the button after a few seconds and go to the terminal:
````
thonny
````
This opens a new window.

At the lower right corner of the window, please click and install MicroPython.
Now chose the Pi Pico WH and newest stable release.
Install the firmware and exit Thonny.


# 1: Install Admiral Squidstat Plus potentiostat
On a Windows X86_64/AMD64 machine install the Admiral Instrument Squidstat software. Afterwards download the Wheel file from here:
https://github.com/Admiral-Instruments/AdmiralSquidstatAPI/tree/main/SquidstatLibrary/windows/pythonWrapper/Release

There is already a working Squidstat Library in this repository which can be used. It is however not updated.
In a terminal within the right python environment, run the command (adjust to your version):
````
pip install SquidstatPyLibrary-1.8.0.5-py3-none-win_amd64.whl
````

# 2: Install Biologic potentiostat
Make sure you have EC-Lab installed on a Windows PC.
In a terminal within the right environment run:
````
pip install biologic-0.4a1-py3-none-any.whl
````

# 3: Install the SDL1_OpenTron_electrodeposition experiment
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
Individual examples can be found in src/python/ where there are some simpler files testing the functionality of the openTron, Arduino, Admiral potentiostat and Biologic potentiostat. For any debugging start with these simple examples.

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

