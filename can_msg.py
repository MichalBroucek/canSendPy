
import struct

can_frame_fmt = "<IB3x8s"

class CanMsg:
    """
    Definition of CAN message
    - id
    - data length
    - flags
    - data[8]
    """

    def __init__(self, msg_id=0, source_addr=0, msg_dlc=0, msg_data=[]):
        self.id = msg_id
        self.source_addr = source_addr
        self.dlc = msg_dlc
        #self.data = [0xFF] * 8  # Raw binary representation #TODO: how to build raw data
        self.data = bytes(msg_data[:msg_dlc])

    def to_string(self):
        bytes_str = ""
        for byte in self.data:
            bytes_str += format(byte, '02X') + " "
        return "" + format(self.id, 'X') + "(" + format(self.source_addr, 'X') + ")" + " " + str(
            self.dlc) + " " + bytes_str.strip()

    def insert_data(self, bin_string):
        """
        Insert binary string data into list of int data
        :return:
        """
        # TODO: ...

    def get_id_to_send(self, first_byte=0x18):
        id_to_send = (first_byte << 24) | self.id
        id_to_send = (id_to_send << 8) | self.source_addr
        return id_to_send.to_bytes(2, byteorder='little')

    def get_binary_can_frame(self):
        """
        Return binary representation of whole CAN frame (to be sent into SocketCan)
        :return:
        """
        # TODO: msg ID + data as bin data ...
        #data = self.data.ljust(8, b'\x00')
        bin_can_frame = struct.pack(can_frame_fmt, self.id, self.dlc, self.data)
        print('BINARY CAN FRAME: ', bin_can_frame)
        return bin_can_frame
