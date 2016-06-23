
class CanMsg:
    """
    Definition of CAN message
    - id
    - data length
    - flags
    - data[8]
    """

    def __init__(self):
        self.id = 0
        self.dlc = 0
        self.data = [0xFF] * 8

    def __init__(self, msg_id, msg_dlc, msg_data):
        self.id = msg_id
        self.dlc = msg_dlc
        self.data = [0xFF] * 8
        self.data = msg_data[:msg_dlc]

    def to_string(self):
        bytes_str = ""
        for byte in self.data:
            bytes_str += byte + " "
        return "" + self.id + " " + self.dlc + " " + bytes_str.strip()


