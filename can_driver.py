
import socket
import struct

#from cansend.can_msg import CanMsg
from can_msg import CanMsg

"""
Format string fmt. for conversion between C struct types and python representation
"""
can_frame_fmt = "<IB3x8s"


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
        self.msg = CanMsg()

    def activate_socket(self):
        """
        Open and bind Socket
        :return:
        """
        self.can_socket.bind((self.can_interface,))

    def deactivate_socket(self):
        """
        Close socket
        :return:
        """
        # TODO: check this behaviour
        self.can_socket.close()

    # @staticmethod
    # def dissect_can_frame(frame):
    #     """
    #     Return python tuple which extracts C struct
    #     :return:
    #     """
    #     can_id, can_dlc, data = struct.unpack(can_frame_fmt, frame)
    #     print('DATA hexdump: ', hexdump.dump(data[:can_dlc], sep=" "))
    #     return can_id, can_dlc, data[:can_dlc]

    def parse_can_frame(self, frame):
        """
        Parse raw can msg representation into CanMsg Python class
        :param frame:
        :return: CanMsg python class
        """
        can_id, can_dlc, data = struct.unpack(can_frame_fmt, frame)
        self.msg.id = (can_id & 0x00FFFFFF) >> 8            # Separate 1st byte (priority) and last byte (source_addr)
        self.msg.source_addr = can_id & 0x000000FF          # Mask out source address
        self.msg.dlc = can_dlc
        self.msg.data = data[:can_dlc]
        print('Received msg: ' + self.msg.to_string())
        return self.msg

    def wait_for_one_msg(self):
        """
        Wait for one can message
        :return: can message
        """
        cf, addr = self.can_socket.recvfrom(16)
        self.parse_can_frame(cf)
        return self.msg

    def wait_for_multi_msg(self):
        """
        Wait for multiple can messages
        :return: list of can messages
        """

    # def build_can_frame(can_id, data):
    #     can_dlc = len(data)
    #     data = data.ljust(8, b'\x00')
    #     return struct.pack(can_frame_fmt, can_id, can_dlc, data)


    def send_one_msg(self, can_msg):
        """
        Send one can message
        :param can_msg: can message to send
        :return: True if msg was sent successfully
        """
        #msg_id_to_send = can_msg.get_id_to_send(0x18)
        binary_can_frame = can_msg.get_binary_can_frame()

        try:
            self.can_socket.send(binary_can_frame)
            #s.send(build_can_frame(0x01, b'\x01\x02\x03'))
        except socket.error:
            print('Error sending CAN frame')

    def send_multi_msg(self, can_msg_list):
        """
        Send list of multi messages
        :param can_msg_list:
        :return:
        """

    # TODO: ...