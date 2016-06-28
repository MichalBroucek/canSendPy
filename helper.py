__author__ = 'brouk'


help_str = """
'canSend.py' - cmd tool to simulate J1939 can-bus processes

Usage: canSend.py [action] [par2 ... par10]

Actions:
  -l --list                                                         Print list of connected devices with information about them.
                                                                      Doesn't work on Linux!
  -s --send_one_message [msgId] [byte1] [byte2] ... [byte8]         Send one specific CAN message with 8 bytes of data.
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

    if len(parameters) == 1:
        print('Wrong number of parameters!')
        print_help()
        return None

    # TODO: try to parse parameter(s)
    if parameters[1] == '--list' or parameters[1] == '-l':
        print('List of can interfaces\nDoesn\'t work on Linux')
    elif parameters[1] == '--send_one_message' or parameters[1] == '-s':
        print('Sending one message')
    elif parameters[1] == '--send_file_messages filename' or parameters[1] == '-f':
        print('send_file_messages filename')
    elif parameters[1] == '--send_default_messages' or parameters[1] == '-d':
        print('send_default_messages')
    elif parameters[1] == '--receive_one_message' or parameters[1] == '-r':
        print('receive_one_message')
    elif parameters[1] == '--receive_messages' or parameters[1] == '-R':
        print('receive_messages')
    elif parameters[1] == '--addr_claim_no_response' or parameters[1] == '-an':
        print('addr_claim_no_response')
    elif parameters[1] == '--addr_claim_addr_used' or parameters[1] == '-au':
        print('addr_claim_addr_used')
    elif parameters[1] == '--addr_claim_addr_used_multi' or parameters[1] == '-aU':
        print('addr_claim_addr_used_multi')
    # TODO: ...
    else:
        print('Unknown parameter(s)\n')
        print_help()

# Actions:
#   -nU --new_device_addr_used_multi [max_timeout] [max_responses]    Initiate new 'Address claim' with the default (FB) addr. as Ehubo2.
#                                                                       Wait [max_timeout] for response(s). Generate [max_responses] Address Collisions
#   -v --vin_code_response       [max_timeout]                        Wait for VIN code request and send VIN code as single message back.
#   -V --vin_code_response_multi [max_timeout]                        Wait for VIN code request and send VIN code as multi frame message back.
#   -h --help                                                         Print this help



def print_help():
    print(help_str)
