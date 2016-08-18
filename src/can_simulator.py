import time
import can

from src import param
from src import candriver
from src import file_io


# TODO: Use constants for Ehubo2 NAME, Default Ehubo2 Address Claim (ID ?, whole msg ?)
# inline FCE for small functions (__ms_to_sedonds, ...)
# Don't use parameters as param is class variable
# use just reference to param OR self.param inside individual methods ... easier to read ...

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
            self.__send_multi_msg(self.param.nmb_msgs, self.param.delay_msg_ms, self.param.msg)
        elif self.param.action in param.SEND_FILE_MSG:
            print('- Sending messages from text file -')
            self.__send_file_messages(self.param.file_name)
        elif self.param.action in param.SEND_DEFAULT:
            print('- Sending default messages -')
            self.__send_default_messages()
        elif self.param.action in param.RECEIVE_ONE_MSG:
            print('- Receiving one message -')
            self.__receive_one_msg(self.param.max_wait_time_ms)
        elif self.param.action in param.RECEIVE_MULTI_MSG:
            print('- Receiving multi messages -')
            self.__receive_multi_msg(self.param.max_wait_time_ms)
        elif self.param.action in param.ADDR_CLAIM_NO_RESPONSE:
            print('- Wait for one Address Claim request and send no response -')
            max_wait_s = self.__ms_to_seconds(self.param.max_wait_time_ms)
            print('Waiting {0} seconds for one \'Address claim\' request message'.format(max_wait_s))
            self.__wait_for_addr_claim_no_collision(self.param.max_wait_time_ms)
        elif self.param.action in param.ADDR_CLAIM_ADDR_USED_MULTI:
            print('- Wait for Address Claim requests and simulate multiple address collisions -')
            collision_count = self.__wait_for_addr_claim_multi_collisions(self.param.max_wait_time_ms,
                                                                          self.param.nmb_msgs)
            print('Address Claim collisions count: {0}'.format(collision_count))
        elif self.param.action in param.NEW_DEV_ADDR_USED_MULTI:
            print('- Connect new device on can-bus and cause multiple address collisions -')
            collision_count = self.__connect_new_device_addr_collisions(self.param.nmb_msgs)
            print('Address Claim collisions count: {0}'.format(collision_count))
        elif self.param.action in param.VIN_CODE_RESPONSE:
            print('- Wait for VIN code request and simulate VIN code response as single frame message -')
            self.__wait_and_reply_VIN_single_frame(self.param.max_wait_time_ms)
        elif self.param.action in param.VIN_CODE_RESPONSE_MULTI:
            print('- Simulate VIN code response as multi frame message -')
            self.__wait_and_reply_VIN_multi_frame(self.param.max_wait_time_ms)
        elif self.param.action in param.ENGINE_SHIFT:
            print('- Simulate Engine shift from {0} RPM ({1} ms) to {2} RPM ({3} ms) -'.format(
                self.param.rpm_value_1, self.param.value_1_ms, self.param.rpm_value_2,
                self.param.value_2_ms))
            self.__simulate_rpm_shift(self.param.rpm_value_1, self.param.value_1_ms, self.param.rpm_value_2,
                                      self.param.value_2_ms)
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
        delay_seconds = self.__ms_to_seconds(delay_ms)
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

    def __send_file_messages(self, file_name):
        """
        Send messages specified in text file
        """
        msg_group_list = file_io.read_messages_from_file(file_name)

        for msg_group in msg_group_list:
            for one_msg in msg_group.messages:
                self.can_bus.send_one_msg(one_msg)

            delay_sec = self.__ms_to_seconds(msg_group.delay)
            time.sleep(delay_sec)

    def __receive_one_msg(self, max_timeout_ms):
        """
        Wait max. time to receive one can msg
        """
        max_time_s = self.__ms_to_seconds(max_timeout_ms)
        print('Waiting for one can message for {0} seconds'.format(max_time_s))
        msg = self.can_bus.wait_for_one_msg(max_time_s)
        print(msg)

    def __receive_multi_msg(self, max_timeout_ms):
        """
        Wait for multiple messages - stop receiving when there are no messages for max_timeout_ms
        :param max_timeout_ms:
        :return:
        """
        max_time_s = self.__ms_to_seconds(max_timeout_ms)
        print('Waiting for multiple can messages maximum for {0} seconds'.format(max_time_s))
        while True:
            msg = self.can_bus.wait_for_one_msg(max_time_s)
            if msg is None:
                break
            print(msg)

    def __wait_for_addr_claim_no_collision(self, max_wait_time_ms):
        """
        Wait max. time for one Address claim request
        :param max_wait_time_ms:
        :return:
        """
        max_time_s = self.__ms_to_seconds(max_wait_time_ms)
        start_time = time.time()
        actual_waiting_time = 0.0

        while actual_waiting_time <= max_time_s:
            msg = self.can_bus.get_one_msg()

            if msg is not None:
                if self.__is_addr_claim_msg(msg.arbitration_id):
                    print(msg)
                    return msg

            actual_waiting_time = time.time() - start_time

        return None

    @staticmethod
    def __is_addr_claim_msg(arbitration_id):
        """
        Check if 'arbitration_id' from can-bus is 'Address Claim' message ID
        :param msg_id:
        :return:
        """
        MSG_ID_MASK = 0x00FF0000
        ADDR_CLAIM_MSG_ID = 0xEE
        masked_msg_id = (MSG_ID_MASK & arbitration_id) >> 16
        if masked_msg_id == ADDR_CLAIM_MSG_ID:
            return True
        else:
            False

    @staticmethod
    def __is_VIN_code_request_msg(msg):
        """
        Check if 'arbitration_id' from can-bus is 'VIN code request' message ID
        :param msg_id:
        :return:
        """
        assert isinstance(msg, can.Message)
        MSG_ID_MASK = 0x00FF0000
        REQUEST_MSG_ID = 0xEA  # J1939 Request message ID
        VIN_CODE_MSG_ID = 0xFEEC
        requested_msg_id = 0  # J1939 msg ID which is requested from network
        masked_msg_id = (MSG_ID_MASK & msg.arbitration_id) >> 16
        if masked_msg_id == REQUEST_MSG_ID:

            requested_msg_id |= msg.data[2] << 16  # 0x00
            requested_msg_id |= msg.data[1] << 8  # 0xFE
            requested_msg_id |= msg.data[0]  # 0xEC

            if requested_msg_id == VIN_CODE_MSG_ID:
                return True
            else:
                return False
        else:
            False

    def __wait_for_addr_claim_multi_collisions(self, max_wait_time_ms, nmb_collisions):
        """
        Wait for 'Address Claim' request and generate/send nmb_msgs Address collisions
        :param max_wait_time_ms:
        :param nmb_collisions:
        :return:
        """
        msg = self.__wait_for_addr_claim_no_collision(max_wait_time_ms)

        if msg is None:
            print('Timeout expired for first \'Address claim\' request')
            return

        # Needs to be higher priority (= smaller number) than Gen2 NAME: 0x00, 0x00, 0x40, 0x32, 0x00, 0xff, 0x02, 0x10
        data_to_send = [0x00, 0x00, 0x40, 0x32, 0x00, 0xff, 0x02, 0x0f]
        # Needs to send back with the same msg ID to create Address Collision
        max_addr_claim_response_delay_ms = 500  # 250ms request + 250ms response TODO: 250 or 500 ? If works with 250 keep 250ms

        actual_collisions_count = 0
        while actual_collisions_count < nmb_collisions:
            addr_collision_response = can.Message(arbitration_id=msg.arbitration_id, extended_id=True,
                                                  data=data_to_send)
            self.__send_one_msg(addr_collision_response)
            actual_collisions_count += 1

            msg = self.__wait_for_addr_claim_no_collision(max_addr_claim_response_delay_ms)
            if msg is None:
                break

        return actual_collisions_count;

    @staticmethod
    def __ms_to_seconds(ms_time):
        """
        Convert time [ms] to time [s]
        :param ms_time:
        :return:
        """
        return ms_time / 1000.0

    def __connect_new_device_addr_collisions(self, nmb_collisions):
        """
        Simulate new device on can-bus which tries to use the same Address as default Ehubo2 address
        :param max_wait_time_ms:
        :param nmb_collisions:
        :return:
        """
        # Address claim ID = EEFFxx + Default Ehubo2 Address is 0xFB (251 dec)
        addr_claim_msg_id = 0x18EEFFFB
        # Data needs to have higher priority (= smaller number) than Gen2 NAME: 0x00, 0x00, 0x40, 0x32, 0x00, 0xff, 0x02, 0x10
        data_to_send = [0x00, 0x00, 0x40, 0x32, 0x00, 0xff, 0x02, 0x0f]
        max_response_waittime_ms = 250
        new_addr_request = can.Message(arbitration_id=addr_claim_msg_id, extended_id=True, data=data_to_send)
        self.__send_one_msg(new_addr_request)
        collision_count = self.__wait_for_addr_claim_multi_collisions(max_response_waittime_ms, nmb_collisions)
        return collision_count + 1  # + 1 first initial request from new device

    def __wait_and_reply_VIN_single_frame(self, max_wait_time_ms):
        """
        Wait for VIN code request and reply by VIN code as single can frame message
        :return:
        """
        msg = self.__wait_for_VIN_code_request(max_wait_time_ms)

        if msg is None:
            print('No \'VIN code\' request received in {0} seconds'.format(self.__ms_to_seconds(max_wait_time_ms)))
            return

        # Build and send VIN code message
        vin_code_msg_id = 0x18FEEC01  # VIN code message = 0xFEEC (see. J1939 standards)
        # ASCII 'V' -> 0x56
        # ASCII 'I' -> 0x49
        # ASCII 'N' -> 0x4E
        # ASCII '1' -> 0x31
        # ASCII '2' -> 0x32
        # ASCII '3' -> 0x33
        # ASCII '*' -> 0x2A     ('*' = end of VIN code)
        # no data   -> 0xFF
        vin_code_data = [0x56, 0x49, 0x4E, 0x31, 0x32, 0x33, 0x2A, 0xFF]
        vin_code_msg = can.Message(arbitration_id=vin_code_msg_id, extended_id=True, data=vin_code_data)
        self.__send_one_msg(vin_code_msg)

    def __wait_and_reply_VIN_multi_frame(self, max_wait_time_ms):
        """
        Wait max. time for VIN code request and reply by VIN code as single can frame message
        :param max_wait_time_ms:
        :return:
        """
        msg = self.__wait_for_VIN_code_request(max_wait_time_ms)

        if msg is None:
            print('No \'VIN code\' request received in {0} seconds'.format(self.__ms_to_seconds(max_wait_time_ms)))
            return

        # Build and send VIN code message as multi-frame can message
        vin_code_multi_messages = self.__get_VIN_code_multi_frame()
        for can_frame in vin_code_multi_messages:
            self.__send_one_msg(can_frame)
            time.sleep(0.050)  # According J1939 std. multi frame messages with 50ms time delay

    def __wait_for_VIN_code_request(self, max_wait_time_ms):
        """
        Wait max. time for one VIN code request message
        :param max_wait_time_ms:
        :return:
        """
        max_time_s = self.__ms_to_seconds(max_wait_time_ms)
        start_time = time.time()
        actual_waiting_time = 0.0

        while actual_waiting_time <= max_time_s:
            #msg = self.can_bus.get_one_msg()
            msg = self.can_bus.wait_for_one_msg(0.005)


            if msg is not None:
                print(msg)
                if self.__is_VIN_code_request_msg(msg):
                    print(msg)
                    return msg

            actual_waiting_time = time.time() - start_time

        return None

    @staticmethod
    def __get_VIN_code_multi_frame():
        """
        Generate VIN code messages as list of multi frame messages
        :return:
        """
        initial_frame_data = [0x20, 0x12, 0x00, 0x03, 0xFF, 0xEC, 0xFE, 0x00]
        initial_frame_msg = can.Message(arbitration_id=0x18ECFF01, extended_id=True, data=initial_frame_data)
        msg1_data = [0x01, 0x56, 0x49, 0x4E, 0x31, 0x32, 0x33, 0x34]
        msg1 = can.Message(arbitration_id=0x18EBFF01, extended_id=True, data=msg1_data)
        msg2_data = [0x02, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 0x31]
        msg2 = can.Message(arbitration_id=0x18EBFF01, extended_id=True, data=msg2_data)
        msg3_data = [0x03, 0x32, 0x33, 0x34, 0x2A, 0xFF, 0xFF, 0xFF]
        msg3 = can.Message(arbitration_id=0x18EBFF01, extended_id=True, data=msg3_data)

        return [initial_frame_msg, msg1, msg2, msg3]

    def __simulate_rpm_shift(self, rpm_1_value, rpm_1_time_ms, rpm_2_value, rpm_2_time_ms):
        """
        Simulate Engine shift from one RPM value to second RPM value for specified time
        """
        rpm_msg_1 = self.__get_EEC1_message(rpm_1_value)  # RPM signal is sent inside EEC1 J1939 message
        rpm_msg_2 = self.__get_EEC1_message(rpm_2_value)
        rpm_1_time_s = self.__ms_to_seconds(rpm_1_time_ms)
        rpm_2_time_s = self.__ms_to_seconds(rpm_2_time_ms)

        print('Sending RPM value: {0} for {1} second(s)'.format(rpm_1_value, rpm_1_time_s))
        self.__keep_sending_message_for_max_time(rpm_msg_1, 20, rpm_1_time_ms)  # Cycle time 20ms (see J1939 std.)
        print('Sending RPM value: {0} for {1} second(s)'.format(rpm_2_value, rpm_2_time_s))
        self.__keep_sending_message_for_max_time(rpm_msg_2, 20, rpm_2_time_ms)  # Cycle time 20ms (see J1939 std.)

    def __keep_sending_message_for_max_time(self, msg_to_send, delay_ms, timeout_ms):
        """
        Keep sending one message for specific time [ms] with specific time cycle [ms]
        :param msg_to_send:
        :param delay_ms:
        :param timeout_ms:
        :return:
        """
        timeout_seconds = self.__ms_to_seconds(timeout_ms)
        delay_seconds = self.__ms_to_seconds(delay_ms)
        start_time = time.time()
        actual_waiting_time = 0.0

        if msg_to_send is not None:
            while actual_waiting_time <= timeout_seconds:
                self.__send_one_msg(msg_to_send)
                time.sleep(delay_seconds)
                actual_waiting_time = time.time() - start_time

    @staticmethod
    def __get_EEC1_message(rpm_value):
        """
        Get J1939 EEC1 message with specific RPM value
        :return:
        """
        eec1_id = 0xCF00401
        rpm_lsb = rpm_msb = 0

        try:
            raw_rpm_value = int(round(rpm_value / 0.125))  # See J1939 std. EEC1 message: 0.125 rpm per bit gain
            rpm_lsb = raw_rpm_value & 0x00FF
            rpm_msb = (raw_rpm_value & 0xFF00) >> 8
        except ValueError:
            print('Error: Cannot convert physical RPM value into raw value for EEC1 message')
            return None

        eec1_data = [0x00, 0x00, 0x00, rpm_lsb, rpm_msb, 0x00, 0x00, 0x00]
        return can.Message(arbitration_id=eec1_id, extended_id=True, data=eec1_data)
