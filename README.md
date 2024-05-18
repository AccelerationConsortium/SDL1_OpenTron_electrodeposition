# SDL1_OpenTron_electrodeposition
This is the repository for the work done by external PhD researcher, Nis Fisker-Bødker from the Danish Technical University (DTU).
The software combines the use of an openTron OT2 and a Sparkfun Arduino to produce a facility for AI optimised electrodeposition of Oxygen Evolution Reaction (OER) catalyst for watersplitting in alkaline environment.

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
