# This script demonstrates how to run an EIS experiment using the PotentiostatAdmiralWrapper class
from .potentiostat_admiral_wrapper import PotentiostatAdmiralWrapper
my_experiment = PotentiostatAdmiralWrapper()
my_experiment.runEISPotentiostatic(100000, 1000, 10, 0.0, 0.1)
