#!/usr/bin/env python3

# TODO:
# Add unit tests for this tool!

import sys
from src import param
from src import can_simulator

#can_interface = 'vcan0'
can_interface = 'can0'

if __name__ == "__main__":
    param = param.Param()
    simulator_parameters = param.parse_cmd_params(sys.argv)

    if simulator_parameters is None:
        exit()

    simulator = can_simulator.CanSimulator(simulator_parameters, can_interface)
    simulator.run_action()

    print("- Done -")
