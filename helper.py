__author__ = 'brouk'

import argparse


class Param:
    """
    Class to hold parameters from command line
    """

    def __init__(self):
        self.function = None
        self.timeout = None
        self.max_msg = None


def parse_cmd_params(parameters):
    """
    Parse command line parameters
    :return: Param object generated from cmd arguments
    """
    # TODO: This is nice but doesn't fit this purpose
    # parser = argparse.ArgumentParser()
    # parser.add_argument("action",
    #                     help="Action to be performed (wait_for_one_msg, wait_for_multi_msgs, send_one_msg, semd_default_msgs, send_file_msgs, ...)")
    # parser.add_argument("max_timeout", type=int, help="Maximum timeout for waiting on can-bus message(s)")
    # parser.add_argument("max_nmb_msgs", type=int, help="maximum number of messages to receive")
    # args = parser.parse_args()

    for param in parameters[1:]:
        print('Param: ', param)
