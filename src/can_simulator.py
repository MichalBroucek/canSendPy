
import time
import can

from src import param
from src import candriver
from src import file_io


class CanSimulator:
    """
    Useful methods to simulate different ECU behavior
    - wait for specific message (timeout)
    - wait for Address Claim request - no collision
    - wait for Address Claim request - one collision
    - wait for Address Claim request - multiple collision
    - wait for Address Claim request - no addresses available
    - wait for new device Address Claim - no collision
    - wait for new device Address Claim - one collision
    - wait for new device Address Claim - multiple collision
    - wait for new device Address Claim - no addresses left
    - wait for VIN code request - VIN code single frame response
    - wait for VIN code request - VIN code multiple frame response
    """

    def __init__(self, cmd_parameters, can_interface):
        self.param = cmd_parameters
        self.interface = can_interface
        self.can_bus = candriver.CanDriver(self.interface)

    def run_action(self):
        """
        Run appropriate simulator action
        :param param:
        :return:
        """
        if self.param.action in param.LIST:
            print('CanSimulator: print out list of devices ? - Not implemented yet!\n')
            print(self.__list())
        elif self.param.action in param.SEND_ONE_MSG:
            print('- Sending one message -')
            self.__send_one_msg(self.param.msg)
        elif self.param.action in param.SEND_MSG_MULTI:
            print('- Sending multiple times one message with specific delay -')
            self.__send_multi_msg(self.param.nmb_msgs, self.param.delay, self.param.msg)
        elif self.param.action in param.SEND_FILE_MSG:
            print('- Sending messages from text file -')
            self.__send_file_messages()
        elif self.param.action in param.SEND_DEFAULT:
            print('- Sending default messages -')
            self.__send_default_messages()
        else:
            print('Unknown action')
            print('Exit')
            return

    def __list(self):
        """
        List parameters for can interface
        """
        return self.can_bus.bus.socket.__str__()

    def __send_one_msg(self, msg_to_send):
        """
        Send one message action
        :param msg_to_send can message to be sent
        """
        self.can_bus.send_one_msg(msg_to_send)
        print(msg_to_send)

    def __send_multi_msg(self, nmb_msgs, delay_ms, msg_to_send):
        """
        Send the same message multiple times
        """
        delay_seconds = delay_ms / 1000.0
        print('Delay between messages: {0} [seconds]'.format(delay_seconds))
        for i in range(nmb_msgs):
            self.can_bus.send_one_msg(msg_to_send)
            print(msg_to_send)
            time.sleep(delay_seconds)

    def __send_default_messages(self):
        """
        Sends default messages
        """
        msg1 = can.Message(arbitration_id=0x18FEF101, extended_id=True, data=([0, 0, 0x32, 0, 0, 0, 0, 0]))
        msg2 = can.Message(arbitration_id=0x0CF00402, extended_id=True, data=([0, 0, 0xAA, 0, 0xAA, 0, 0, 0]))
        messages = [msg1, msg2]

        for msg in messages:
            self.can_bus.send_one_msg(msg)
            print(msg)
            time.sleep(0.01)

    def __send_file_messages(self):
        """
        Send messages specified in text file
        """
        msg_group_list = file_io.read_messages_from_file(self.param.file_name)

        for msg_group in msg_group_list:
            for one_msg in msg_group.messages:
                self.can_bus.send_one_msg(one_msg)

            delay_sec = msg_group.delay / 1000.0
            time.sleep(delay_sec)
