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
        self.data = [0xFF] * 8  # Raw binary representation #TODO: how to build raw data
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

    # def get_bin_data(self):
    #     """
    #     Return binary representation of data
    #     :return:
    #     """
    #     # TODO: ... get bin data as Python bin string ...
    #     bin_data = bytes(self.data)
    #     return bin_data
