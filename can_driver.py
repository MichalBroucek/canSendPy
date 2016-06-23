
import socket
import struct

class Can_driver:
    """
    Class to handle Socket can-bus interface
    - open Socket can interface
    - close Socket can interface
    - wait for one can message (with timeout)
    - wait for multiple can messages (with timeout)
    - send one can message
    - send list of messages (no delays)
    - send list of messages (with delays)
    """

    def __init__(self, interface_name):
        # TODO: ...
        # Do initialization of Socket here ?
        self.can_socket = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.can_interface = interface_name

    def activate_socket(self, can_interface):
        """
        Open and bind Socket
        :return:
        """
        self.can_socket.bind(self.can_interface)

    def deactivate_socket(self):
        """
        Close socket
        :return:
        """
        # TODO: check this behaviour
        self.can_socket.close()

    def wait_for_one_msg(self):
        """
        Wait for one can message
        :return: can message
        """
        # self.can_socket.recvfrom(16)


    def wait_for_multi_msg(self):
        """
        Wait for multiple can messages
        :return: list of can messages
        """

    def send_one_msg(self, can_msg):
        """
        Send one can message
        :param can_msg: can message to send
        :return: True if msg was sent successfully
        """

    def send_multi_msg(self, can_msg_list):
        """
        Send list of multi messages
        :param can_msg_list:
        :return:
        """

    # TODO: ...