
import can


class CanDriver:
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

    def __init__(self, can_channel):
        self.channel = can_channel
        self.msg = can.Message()

        try:
            self.bus = can.interface.Bus(channel=can_channel, bustype='socketcan_native')
        except OSError:
            self.bus = None
            print('Error: No SocketCan device found!\nBus is not initialized!')

    def wait_for_one_msg(self, max_timeout_seconds):
        """
        Wait for one can message
        :return: can message
        """
        msg = self.bus.recv(max_timeout_seconds)
        #assert isinstance(msg, can.Message)
        return msg

    def get_one_msg(self):
        """
        Get actual message from can-bus
        :return:
        """
        msg = self.bus.recv(0.0)
        return msg

    def send_one_msg(self, can_msg):
        """
        Send one can message
        :param can_msg: can message to send
        :return: True if msg was sent successfully
        """
        assert isinstance(can_msg, can.Message)
        self.bus.send(can_msg)
