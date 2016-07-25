#!/usr/bin/env python3

# TODO:
# 1. print out message which is sent
# 2. implement missing functionality - from original canSend (with different parameters ...)
# 3. Add unit tests for this tool!

import sys
#import can
#from src import candriver
from src import helper
from src import can_simulator

can_interface = 'vcan0'

if __name__ == "__main__":
    # Example of usage
    # can_handler = Can_driver(can_interface)
    # msg = can.Message(arbitration_id=0x18FEF101, extended_id=True, data=([0x11] * 8))
    # can_handler.send_one_msg(msg)  # Sending 5 messages
    # can_handler.wait_for_one_msg()      # Receiving 5 messages

    # 1. Parse command line parameters
    # 2. Call appropriate action
    # 3. Generate output cmd, file, ...

    # 1. todo: Needs to complete all actions for all parameters
    param = helper.Param()
    simulator_parameters = param.parse_cmd_params(sys.argv)

    if simulator_parameters is None:
        exit()

    simulator = can_simulator.CanSimulator(simulator_parameters, can_interface)
    simulator.run_action()

    print("Done")
