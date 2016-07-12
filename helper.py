__author__ = 'brouk'

import can

help_str = """
'canSend.py' - cmd tool to simulate J1939 can-bus processes

Usage: canSend.py [action] [par2 ... par10]

Actions:
  -l --list                                                         Print list of connected devices with information about them.
                                                                      Doesn't work on Linux!
  -s --send_one_message [msgId] [byte1] [byte2] ... [byte8]         Send one specific CAN message with 8 bytes of data.
  -S --send_message_multi [nmb_msg] [delay] [msgId] [byte1] [byte2] ... [byte8]   Send the same CAN message with 8 bytes of data multiple times.
  -f --send_file_messages [filename]                                Send messages defined in the text file. Format of file is:
                                                                      18fef100 21 21 21 21 21 21 21 21
                                                                      cf00400 22 22 22 22 22 22 22 22
                                                                      delay 700
                                                                      18fef100 31 31 31 31 31 31 31 31
                                                                      delay 800
  -d --send_default_messages                                        Send default messages.
  -r --receive_one_message    [max_timeout]                         Wait [ms] for one message for specific number of milliseconds.
  -R --receive_messages       [max_timeout]                         Wait [ms] for all messages for specific number of milliseconds.
  -an --addr_claim_no_response [max_timeout]                        Wait [ms] for 'Address claim message' send no response (address can be used).
  -au --addr_claim_addr_used   [max_timeout]                        Wait [ms] for 'Address claim message' send 'Address claimed' response (address can NOT be used).
  -aU --addr_claim_addr_used_multi [max_timeout] [max_responses]    Wait max [ms] for 'Address claim' and response by [max_responses] nmb. of Addr. Claimed msgs.
  -nU --new_device_addr_used_multi [max_timeout] [max_responses]    Initiate new 'Address claim' with the default (FB) addr. as Ehubo2.
                                                                      Wait [max_timeout] for response(s). Generate [max_responses] Address Collisions
  -v --vin_code_response       [max_timeout]                        Wait for VIN code request and send VIN code as single message back.
  -V --vin_code_response_multi [max_timeout]                        Wait for VIN code request and send VIN code as multi frame message back.
  -h --help                                                         Print this help
Examples:
    canSend.py send_one_message 18FEF100 01 02 03 04 05 06 07 08
    canSend.py send_file_messages ~/workspace_sandbox/canSend/Debug/CanData.txt
"""

# Action constants
LIST = ["-l", "--list"]
SEND_ONE_MSG = ["-s", "--send_one_message"]
SEND_MSG_MULTI = ["-S", "--send_message_multi"]
SEND_FILE_MSG = ["-f", "--send_file_messages"]
SEND_DEFAULT = ["-d", "--send_default_messages"]
RECEIVE_ONE_MSG = ["-r", "--receive_one_message"]
RECEIVE_MULTI_MSG = ["-R", "--receive_messages"]
ADDR_CLAIM_NO_RESPONSE = ["-an", "--addr_claim_no_response"]
ADDR_CLAIM_ADDR_USED = ["-au", "--addr_claim_addr_used"]
ADDR_CLAIM_ADDR_USED_MULTI = ["-aU", "--addr_claim_addr_used_multi"]
NEW_DEV_ADDR_USED_MULTI = ["-nU", "--new_device_addr_used_multi"]
VIN_CODE_RESPONSE = ["-v", "--vin_code_response"]
VIN_CODE_RESPONSE_MULTI = ["-V", "--vin_code_response_multi"]
HELP = ["-h", "--help"]

class Param:
    """
    Class to hold parameters from command line
    """
    def __init__(self):
        self.action = None
        self.timeout = None
        self.nmb_msgs = None
        self.delay = None
        self.msg = None

# Helper functions to parse cmd line arguments parametrs

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

    if len(parameters) == 1:
        print('Wrong number of parameters!')
        print_help()
        exit()

    action_param = None

    if parameters[1] in LIST:
        print('Active interface - details')
        action_param = parse_interface_info_param(parameters[1:])
    elif parameters[1] in SEND_ONE_MSG:
        print('- Sending one message -')
        action_param = parse_one_msg_param(parameters[1:])
    elif parameters[1] in SEND_MSG_MULTI:
        print('- Sending multiple times one message with specific delay -')
        action_param = parse_multi_msg_param(parameters[1:])
    elif parameters[1] in SEND_FILE_MSG:
        print('send_file_messages filename')
    elif parameters[1] in SEND_DEFAULT:
        print('send_default_messages')
    elif parameters[1] in RECEIVE_ONE_MSG:
        print('receive_one_message')
    elif parameters[1] in RECEIVE_MULTI_MSG:
        print('receive_messages')
    elif parameters[1] in ADDR_CLAIM_NO_RESPONSE:
        print('addr_claim_no_response')
    elif parameters[1] in ADDR_CLAIM_ADDR_USED:
        print('addr_claim_addr_used')
    elif parameters[1] in ADDR_CLAIM_ADDR_USED_MULTI:
        print('addr_claim_addr_used_multi')
    elif parameters[1] in NEW_DEV_ADDR_USED_MULTI:
        print('new_device_addr_used_multi')
    elif parameters[1] in VIN_CODE_RESPONSE:
        print('vin_code_response')
    elif parameters[1] in VIN_CODE_RESPONSE_MULTI:
        print('vin_code_response_multi')
    else:
        print('Unknown action\n')
        print_help()

    if action_param is None:
        print('Wrong parameter(s) or this functionality is not implemented yet.')
        exit()

    return action_param


def print_help():
    print(help_str)


def get_msg_from_argv_list(argv_list):
    """
    Get can message from hex string msgId and list of individual bytes as strings
    :param argv: [msgId Byte1 Byte2 Byte3 Byte4 Byte5 Byte6 Byte7 Byte8]
    :return: can.Message
    """
    if len(argv_list) != 9:
        print('Wrong number of parameters for building can Message from msgId and list of string bytes!')
        print_help()
        return None

    msgid_int = int(argv_list[0], 0)
    data_list_int = [int(x, 16) for x in argv_list[1:]]

    msg = can.Message(extended_id=True, arbitration_id=msgid_int, data=data_list_int)
    #print(msg)
    return msg


def get_msg_from_argvs(argvs):
    """
    Get can message from hex string msgId and hex bytes as one long string
    :param argvs: [msgId Byte1Byte2Byte3Byte4Byte5Byte6Byte7Byte8]
    :return: can.Message
    """
    if len(argvs) != 2:
        print('Wrong number of parameters for building can Message from msgId and string of bytes data!')
        print_help()
        return None

    msgid_int = int(argvs[0], 0)
    data_list_int = bytearray(argvs[1].decode('hex'))
    msg = can.Message(extended_id=True, arbitration_id=msgid_int, data=data_list_int)
    #print(msg)
    return msg


def parse_one_msg_param(parameters):
    """
    Parse cmd arguments for send_one_message
    :param list: [action msg_id byte1 byte2 byte3 byte4 byte5 byte6 byte7 byte8]
    :return: Param()
    """
    if len(parameters) != 10:
        print('Wrong number of parameters for sending one can message')
        print_help()
        return None

    param = Param()
    param.action = parameters[0]
    param.msg = get_msg_from_argv_list(parameters[1:])
    #param.msg = get_msg_from_argvs(parameters[1:])
    return param


def parse_multi_msg_param(parameters):
    """
    Parse cmd arguments for send_message_multi
    :param list: [action nmb_msgs delay_ms msg_id byte1 byte2 byte3 byte4 byte5 byte6 byte7 byte8]
    :return: Param()
    """
    if len(parameters) != 12:
        print('Wrong number of parameters for sending one can message')
        print_help()
        return None

    param = Param()
    param.action = parameters[0]
    param.nmb_msgs = str_to_digit(parameters[1])
    param.delay = str_to_digit(parameters[2])
    param.msg = get_msg_from_argv_list(parameters[3:])
    return param


def parse_interface_info_param(parameters):
    """
    Parse parameter for interface info
    :param parameters:
    :return:
    """
    if len(parameters) != 1:
        print('Wrong number of parameters for listing interface info!')
        print_help()
        return None

    param = Param()
    param.action = parameters[0]
    return param


def str_to_digit(positive_int_str):
    """
    Get positive integer from string
    :param positive_int_str:
    :return: int
    """
    if positive_int_str.isdigit():
        return int(positive_int_str)
    else:
        print('Error: Value \'{0}\' is not string representation of positive integer!\n'.format(positive_int_str))
        return None


def str_to_float(float_str):
    """
    Get float number from string
    :param float_str:
    :return: float
    """
    try:
        return float(float_str)
    except ValueError:
        print('Error: Value \'{0}\' is not string representation of float!\n'.format(float_str))
