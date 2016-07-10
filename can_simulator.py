
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
        if self.param.action in helper.LIST:
            print('CanSimulator: print out list of devices ? - Not implemented yet!')
        elif self.param.action in helper.SEND_ONE_MSG:
            print('CanSimulator: Sending one message ...')
            self.__send_one_msg(self.param)
        elif self.param.action in helper.SEND_MSG_MULTI:
            print('CanSimulator: Sending multi messages ...')
        elif self.param.action in helper.SEND_FILE_MSG:
            print('CanSimulator: Sending messages from file ...')
        elif self.param.action in helper.SEND_DEFAULT:
            print('CanSimulator: Sending default messages ...')
        else:
            print('Unknown action')
            print('Exit')
            return

    def __send_one_msg(self, param):
        """
        Send one message action
        :param param:
        :return:
        """
        # TODO: ...
        # self.can_bus.send_one_msg()
        pass

