__author__ = 'brouk'

import can

# INTERFACE FOR WIN - SAME HAS TO BE IMPLEMENTED here
# 	cout << "  list                                                        Print list of connected devices with information about them." << endl;
# DONE 	cout << "  send_one_message msgId byte1 byte2 ... byte8                Send one specific CAN message with 8 bytes of data." << endl;
# 	cout << "  send_file_messages fileName                                 Send messages defined in the text file. Format of file is:" << endl;
# 	cout << "                                                                18fef100 21 21 21 21 21 21 21 21" << endl;
# 	cout << "                                                                cf00400 22 22 22 22 22 22 22 22" << endl;
# 	cout << "                                                                delay 700" << endl;
# 	cout << "                                                                18fef100 31 31 31 31 31 31 31 31" << endl;
#     cout << "                                                                delay 800" << endl;
# DONE	cout << "  send_default_messages                                       Send default messages." << endl;
# 	cout << "  receive_one_message    [max_timeout]                        Wait [ms] for one message for specific number of milliseconds." << endl;
# 	cout << "  receive_messages       [max_timeout]                        Wait [ms] for all messages for specific number of milliseconds." << endl;
# 	cout << "  addr_claim_no_response [max_timeout]                        Wait [ms] for 'Address claim message' send no response (address can be used)." << endl;
# 	cout << "  addr_claim_addr_used   [max_timeout]                        Wait [ms] for 'Address claim message' send 'Address claimed' response (address can NOT be used)." << endl;
# 	cout << "  addr_claim_addr_used_multi [max_timeout] [max_responses]    Wait max [ms] for 'Address claim' and response by [max_responses] nmb. of Addr. Claimed msgs." << endl;
# 	cout << "  new_device_addr_used_multi [max_timeout] [max_responses]    Initiate new 'Address claim' with the default (FB) addr. as Ehubo2." << endl;
# 	cout << "                                                                Wait [max_timeout] for response(s)" << endl;
# 	cout << "                                                                Generate [max_responses] Address Collisions" << endl;
# 	cout << "  vin_code_response       [max_timeout]                       Wait for VIN code request and send VIN code as single message back." << endl;
# 	cout << "  vin_code_response_multi [max_timeout]                       Wait for VIN code request and send VIN code as multi frame message back." << endl;
# 	cout << "  help                                                        Print this help." << endl;
# 	cout << "\nExamples:" << endl;
# 	cout << "canSend.exe send_one_message 18FEF100 01 02 03 04 05 06 07 08" << endl;
# 	cout << "canSend.exe send_file_messages c:\\workspace_sandbox\\canSend\\Debug\\CanData.txt" << endl;
# }


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
LIST = ("-l", "--list")
SEND_ONE_MSG = ("-s", "--send_one_message")
SEND_MSG_MULTI = ("-S", "--send_message_multi")
SEND_FILE_MSG = ("-f", "--send_file_messages")
SEND_DEFAULT = ("-d", "--send_default_messages")
RECEIVE_ONE_MSG = ("-r", "--receive_one_message")
RECEIVE_MULTI_MSG = ("-R", "--receive_messages")
ADDR_CLAIM_NO_RESPONSE = ("-an", "--addr_claim_no_response")
ADDR_CLAIM_ADDR_USED = ("-au", "--addr_claim_addr_used")
ADDR_CLAIM_ADDR_USED_MULTI = ("-aU", "--addr_claim_addr_used_multi")
NEW_DEV_ADDR_USED_MULTI = ("-nU", "--new_device_addr_used_multi")
VIN_CODE_RESPONSE = ("-v", "--vin_code_response")
VIN_CODE_RESPONSE_MULTI = ("-V", "--vin_code_response_multi")
HELP = ("-h", "--help")


class Param:
    """
    Class to parse and hold parameters from command line
    """

    def __init__(self):
        self.action = None
        self.timeout = None
        self.nmb_msgs = None
        self.delay_ms = None
        self.max_wait_time_ms = None
        self.msg = None
        self.file_name = None

    def parse_cmd_params(self, parameters):
        """
        Parse command line parameters
        :return: Param object generated from cmd arguments
        """
        if len(parameters) == 1:
            print('Wrong number of parameters!')
            self.print_help()
            return None

        action_param = None

        if parameters[1] in LIST:
            action_param = self.parse_interface_info_param(parameters[1:])
        elif parameters[1] in SEND_ONE_MSG:
            action_param = self.parse_one_msg_param(parameters[1:])
        elif parameters[1] in SEND_MSG_MULTI:
            action_param = self.parse_multi_msg_param(parameters[1:])
        elif parameters[1] in SEND_FILE_MSG:
            action_param = self.parse_file_messages(parameters[1:])
        elif parameters[1] in SEND_DEFAULT:
            action_param = self.parse_send_default_param(parameters[1:])
        elif parameters[1] in RECEIVE_ONE_MSG:
            action_param = self.parse_receive_one_msg(parameters[1:])
        # elif parameters[1] in RECEIVE_MULTI_MSG:
        #     pass
        # elif parameters[1] in ADDR_CLAIM_NO_RESPONSE:
        #     pass
        # elif parameters[1] in ADDR_CLAIM_ADDR_USED:
        #     pass
        # elif parameters[1] in ADDR_CLAIM_ADDR_USED_MULTI:
        #     pass
        # elif parameters[1] in NEW_DEV_ADDR_USED_MULTI:
        #     pass
        # elif parameters[1] in VIN_CODE_RESPONSE:
        #     pass
        # elif parameters[1] in VIN_CODE_RESPONSE_MULTI:
        #     pass
        else:
            print('Unknown action!\n')
            self.print_help()
            return None

        if action_param is None:
            print('Wrong parameter(s) or this functionality is not implemented yet.')
            return None

        return action_param

    @staticmethod
    def print_help():
        print(help_str)

    def get_msg_from_argv_list(self, argv_list):
        """
        Get can message from hex string msgId and list of individual bytes as strings
        :param argv_list: [msgId Byte1 Byte2 Byte3 Byte4 Byte5 Byte6 Byte7 Byte8]
        :return: can.Message
        """
        if len(argv_list) != 9:
            print('Wrong number of parameters for building can Message from msgId and list of string bytes!')
            self.print_help()
            return None

        msgid_int = int(argv_list[0], 0)
        data_list_int = [int(x, 16) for x in argv_list[1:]]

        msg = can.Message(extended_id=True, arbitration_id=msgid_int, data=data_list_int)
        # print(msg)
        return msg

    def get_msg_from_argvs(self, argvs):
        """
        Get can message from hex string msgId and hex bytes as one long string
        :param argvs: [msgId Byte1Byte2Byte3Byte4Byte5Byte6Byte7Byte8]
        :return: can.Message
        """
        if len(argvs) != 2:
            print('Wrong number of parameters for building can Message from msgId and string of bytes data!')
            self.print_help()
            return None

        msgid_int = int(argvs[0], 0)
        data_list_int = bytearray(argvs[1].decode('hex'))
        msg = can.Message(extended_id=True, arbitration_id=msgid_int, data=data_list_int)
        # print(msg)
        return msg

    def parse_one_msg_param(self, parameters):
        """
        Parse cmd arguments for send_one_message
        :param parameters:
        :param parameters: [action msg_id byte1 byte2 byte3 byte4 byte5 byte6 byte7 byte8]
        :return: Param() object
        """
        if len(parameters) != 10:
            print('Wrong number of parameters for sending one can message')
            self.print_help()
            return None

        param = Param()
        param.action = parameters[0]
        param.msg = self.get_msg_from_argv_list(parameters[1:])
        # param.msg = self.get_msg_from_argvs(parameters[1:])
        return param

    def parse_multi_msg_param(self, parameters):
        """
        Parse cmd arguments for send_message_multi
        :param parameters:
        :return: Param() object
        """
        if len(parameters) != 12:
            print('Wrong number of parameters for sending one can message')
            self.print_help()
            return None

        param = Param()
        param.action = parameters[0]
        param.nmb_msgs = self.__str_to_digit(parameters[1])
        param.delay_ms = self.__str_to_digit(parameters[2])
        param.msg = self.get_msg_from_argv_list(parameters[3:])
        return param

    def parse_interface_info_param(self, parameters):
        """
        Parse parameter for interface info
        :param parameters:
        :return: Param() object
        """
        if len(parameters) != 1:
            print('Wrong number of parameters for listing interface info!')
            self.print_help()
            return None

        param = Param()
        param.action = parameters[0]
        return param

    def parse_file_messages(self, parameters):
        """
        Parse parameters for sending messages from text file
        :param parameters:
        :return: Param() object
        """
        if len(parameters) != 2:
            print('Wrong number of parameters for sending messages! from text file!')
            self.print_help()
            return None

        param = Param()
        param.action = parameters[0]
        param.file_name = parameters[1]
        return param

    def parse_send_default_param(self, parameters):
        """
        Parse parameters for sending default messages
        :param parameters:
        :return: Param() object
        """
        if not self.__is_right_nmb_of_parameters(parameters, 1,
                                                 'Wrong number of parameters for sending default messages!'):
            return None

        param = Param()
        param.action = parameters[0]
        return param

    def parse_receive_one_msg(self, parameters):
        """
        Parse parameters for receving one msg
        :param parameters:
        :return:
        """
        if not self.__is_right_nmb_of_parameters(parameters, 2,
                                                 'Wrong number of parameters to receive one message!'):
            return None

        param = Param()
        param.action = parameters[0]

        try:
            param.max_wait_time_ms = int(parameters[1])
        except ValueError:
            print('Cannot parse max_timeout parameter!')
            return None

        return param

    def __is_right_nmb_of_parameters(self, parameters, parameters_number, message):
        """
        Check number of parameters
        :return:
        """
        if len(parameters) != parameters_number:
            print(message)
            self.print_help()
            return False
        else:
            return True

    @staticmethod
    def __str_to_digit(positive_int_str):
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

    @staticmethod
    def __str_to_float(float_str):
        """
        Get float number from string
        :param float_str:
        :return: float
        """
        try:
            return float(float_str)
        except ValueError:
            print('Error: Value \'{0}\' is not string representation of float!\n'.format(float_str))
