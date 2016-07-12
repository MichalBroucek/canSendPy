
import time

import helper
import can_driver


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
        self.can_bus = can_driver.Can_driver(self.interface)

    def run_action(self):
        """
        Run appropriate simulator action
        :param param:
        :return:
        """
        print('Param action: {0}'.format(self.param.action))
        if self.param.action in helper.LIST:
            print('CanSimulator: print out list of devices ? - Not implemented yet!\n')
            print(self.__list())
        elif self.param.action in helper.SEND_ONE_MSG:
            print('CanSimulator: Sending one message ...')
            self.__send_one_msg(self.param.msg)
        elif self.param.action in helper.SEND_MSG_MULTI:
            print('CanSimulator: Sending multi messages ...')
            self.__send_multi_msg(self.param.nmb_msgs, self.param.delay, self.param.msg)
        elif self.param.action in helper.SEND_FILE_MSG:
            print('CanSimulator: Sending messages from file ...')
        elif self.param.action in helper.SEND_DEFAULT:
            print('CanSimulator: Sending default messages ...')
        else:
            print('Unknown action')
            print('Exit')
            return

    def __list(self):
        """
        List parameters for can interface
        :return:
        """
        return self.can_bus.bus.socket.__str__()

    def __send_one_msg(self, msg_to_send):
        """
        Send one message action
        :param param:
        :return:
        """
        self.can_bus.send_one_msg(msg_to_send)
        pass

    def __send_multi_msg(self, nmb_msgs, delay_ms, msg_to_send):
        """
        Send the same message multiple times
        :return:
        """
        delay_seconds = delay_ms / 1000.0
        print('Delay between messages: {0} [seconds]'.format(delay_seconds))
        for i in range(nmb_msgs):
            self.can_bus.send_one_msg(msg_to_send)
            time.sleep(delay_seconds)

