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


# 1: Install Admiral Squidstat potentiostat
On a Windows X86_64/AMD64 machine install the Admiral Instrument Squidstat software. Afterwards download the Wheel file from here:
https://github.com/Admiral-Instruments/AdmiralSquidstatAPI/tree/main/SquidstatLibrary/windows/pythonWrapper/Release

In a terminal with the right python environment, run the command (adjust to your version):
````
pip install SquidstatPyLibrary-1.8.0.5-py3-none-win_amd64.whl
````

# 2: Install the openTron wrapper
In a terminal with the correct python environment run:
````
git clone https://github.com/dpersaud/opentronsHTTPAPI_wrapper.git
cd opentronsHTTPAPI_wrapper
pip install -e .
````

# 3: Install the SDL1_OpenTron_electrodeposition experiment
In a terminal with the correct python environment run:
````
git clone https://github.com/AccelerationConsortium/SDL1_OpenTron_electrodeposition.git
cd SDL1_OpenTron_electrodeposition
pip install -e .
````