import time
import can
import subprocess

import canSend
from src import param
from src import candriver
from src import file_io
from src.eld_simulation import ELD_simulation
from src.eld_msg_group import ELD_msg_group


class CanSimulator:
    """
    Methods to simulate different ECU behavior (wait for one or multi can msg, send one or multi msg, sending messages
    from file, address collision simulations, VIN code responses, engine RPM simulations, ...)
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
            print('CanSimulator: print out device info')
            self.__list()
        elif self.param.action in param.BAUDRATE:
            if self.param.baudrate is None:
                print('- Printing actual baud rate -')
                self.__print_actual_baudrate()
            else:
                print('- Setting actual baud rate -')
                self.__set_baudrate(self.param.baudrate)
        elif self.param.action in param.SEND_ONE_MSG:
            print('- Sending one message -')
            self.__send_one_msg(self.param.msg, print_msg_flag=True)
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
            self.__wait_for_addr_claim_no_collision_continuous(self.param.max_wait_time_ms)
        elif self.param.action in param.ADDR_CLAIM_ADDR_USED_MULTI:
            print('- Wait for Address Claim requests and simulate multiple address collisions -')
            collision_count = self.__wait_for_addr_claim_multi_collisions_continuous(self.param.max_wait_time_ms,
                                                                                     self.param.nmb_msgs)
            print('Address Claim collisions count: {0}'.format(collision_count))
        elif self.param.action in param.NEW_DEV_ADDR_USED_MULTI:
            print('- Connect new device on can-bus and cause multiple address collisions -')
            collision_count = self.__new_device_addr_collisions_multi_continuous(self.param.max_wait_time_ms,
                                                                                 self.param.nmb_msgs)
            print('Address Claim collisions count: {0}'.format(collision_count))
        elif self.param.action in param.VIN_CODE_RESPONSE:
            print('- Wait for VIN code request and simulate VIN code response as single frame message -')
            self.__wait_and_reply_VIN_single_frame(self.param.max_wait_time_ms)
        elif self.param.action in param.VIN_CODE_RESPONSE_MULTI:
            print('- Simulate VIN code response as multi frame message -')
            self.__wait_and_reply_VIN_multi_frame(self.param.max_wait_time_ms)
        elif self.param.action in param.ENGINE_HOURS:
            print('- Simulate engine hours response -')
            self.__wait_and_reply_engine_hours(self.param.max_wait_time_ms)
        elif self.param.action in param.ENGINE_SHIFT:
            print('- Simulate Engine shift from {0} RPM ({1} ms) to {2} RPM ({3} ms) -'.format(
                self.param.rpm_value_1, self.param.value_1_ms, self.param.rpm_value_2,
                self.param.value_2_ms))
            self.__simulate_rpm_shift(self.param.rpm_value_1, self.param.value_1_ms, self.param.rpm_value_2,
                                      self.param.value_2_ms)
        elif self.param.action in param.INSTALL_WIZARD_VIN:
            print('- Wait for VIN code request and simulate VIN code response when broadcasting F004 (Engine r.p.m.) '
                  'message -')
            self.__broadcast_and_reply_VIN_multi_frame(self.param.max_wait_time_ms)
        elif self.param.action in param.ELD_MSGS_SIMULATION:
            print(
                '- Simulating ELD messages (Speed, Engine r.p.m., Distance, Engine hours (on request), '
                'VIN code (on request) ) -')
            self.__eld_simulation_default(self.param.max_wait_time_ms)
        elif self.param.action in param.ELD_MSGS_FILE_SIMULATION:
            print('- Simulating ELD messages specified in text file -')
            self.__eld_file_simulation(self.param.file_name)
        elif self.param.action in param.SPEED_SHIFT:
            print('- Simulating Vehicle Speed Shift -')
            self.__simulate_speed_shift(self.param.speed_value1, self.param.value_1_ms, self.param.speed_value2,
                                        self.param.value_2_ms)
        else:
            print('Unknown action')
            print('Exit')
            return

    def __list(self):
        """
        List parameters for can interface
        """
        if self.can_bus.bus is None:
            print('Error: No SocketCan device connected!')
            return

        dev_info = self.can_bus.bus.socket
        if dev_info is None:
            print('Error: No socket for can device available!')
        else:
            print(dev_info.__str__())
        return

    def __print_actual_baudrate(self):
        """
        Print actual baudrate via bash 'ip' command
        # ip -details -statistics link show can0
        :return:
        """
        stdoutdata = subprocess.getoutput("ip -details -statistics link show can0")
        baudrate_str = stdoutdata.split('bitrate ')[1]
        baudrate_str = baudrate_str.split(' ')[0]
        print('Baud rate: {0}'.format(baudrate_str))

    def __set_baudrate(self, baud_rate):
        """
        Set can-bus baud rate via bash 'ip' command
        # sudo ip link set can0 down
        # sudo ip link set can0 type can bitrate 500000
        # sudo ip link set can0 up
        :return:
        """
        response = subprocess.call(["sudo", "ip", "link", "set", canSend.can_interface, "down"])
        if response != 0:
            print("Error: Cannot deactivate '{0}' interface".format(canSend.can_interface))
            print(response)
        response = subprocess.call(
            ["sudo", "ip", "link", "set", canSend.can_interface, "type", "can", "bitrate", str(baud_rate)])
        if response != 0:
            print("Error: Cannot set {0} baudrate for interface '{1}'".format(baud_rate, canSend.can_interface))
            print(response)
        response = subprocess.call(["sudo", "ip", "link", "set", canSend.can_interface, "up"])
        if response != 0:
            print("Error: Cannot eactivate '{0}' interface".format(canSend.can_interface))
            print(response)
        self.__print_actual_baudrate()

    def __send_one_msg(self, msg_to_send, print_msg_flag=False):
        """
        Send one message action
        :param msg_to_send can message to be sent
        """
        self.can_bus.send_one_msg(msg_to_send)
        if print_msg_flag:
            self.__print_msg(msg_to_send, received=False)

    def __send_one_msg_no_printout(self, msg_to_send):
        """
        Send one message action
        :param msg_to_send can message to be sent
        """
        self.can_bus.send_one_msg(msg_to_send)

    def __send_multi_msg(self, nmb_msgs, delay_ms, msg_to_send):
        """
        Send the same message multiple times
        """
        delay_seconds = self.__ms_to_seconds(delay_ms)
        print('Delay between messages: {0} [seconds]'.format(delay_seconds))
        for i in range(nmb_msgs):
            self.__print_msg(msg_to_send, received=False)
            self.can_bus.send_one_msg(msg_to_send)
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
            self.__print_msg(msg, received=False)
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
        self.__print_msg(msg)

    def __receive_multi_msg(self, max_timeout_ms):
        """
        Wait for multiple messages - stop receiving when there are no messages for max_timeout_ms
        :param max_timeout_ms:
        :return:
        """
        max_time_s = self.__ms_to_seconds(max_timeout_ms)
        actual_waiting_time = 0
        start_time = time.time()
        while actual_waiting_time <= max_time_s:
            msg = self.can_bus.wait_for_one_msg(0.05)

            if msg is not None:
                if self.__is_addr_claim_msg(msg.arbitration_id):
                    self.__print_msg(msg)

            actual_waiting_time = time.time() - start_time

    def __wait_for_addr_claim(self, max_wait_time_ms):
        """
        Wait max. time for one Address claim request
        :param max_wait_time_ms:
        :return:
        """
        max_time_s = self.__ms_to_seconds(max_wait_time_ms)
        start_time = time.time()
        actual_waiting_time = 0.0

        description = "ELD broadcast msgs for Address claim simulation"
        msg_group = ELD_msg_group(description, 10, 600, 10500, 1000, None, None)

        while actual_waiting_time <= max_time_s:
            # J1939 messages need to be broadcast for Address claim Ehubo2 mechanism
            self.__send_eld_broadcast_mesages(msg_group)
            msg = self.can_bus.wait_for_one_msg(0.05)

            if msg is not None:
                if self.__is_addr_claim_msg(msg.arbitration_id):
                    self.__print_msg(msg)
                    return msg

            actual_waiting_time = time.time() - start_time

        return None

    def __wait_for_addr_claim_no_collision_continuous(self, max_wait_time_ms):
        """
        Wait max. time for one Address claim requests
        :param max_wait_time_ms:
        :return:
        """
        max_time_s = self.__ms_to_seconds(max_wait_time_ms)
        start_time = time.time()
        actual_waiting_time = 0.0

        description = "ELD broadcast msgs for Address claim simulation"
        msg_group = ELD_msg_group(description, 10, 600, 10500, 1000, None, None)

        while actual_waiting_time <= max_time_s:
            # J1939 messages need to be broadcast for Address claim Ehubo2 mechanism
            self.__send_eld_broadcast_mesages(msg_group)
            msg = self.can_bus.wait_for_one_msg(0.05)

            if msg is not None:
                if self.__is_addr_claim_msg(msg.arbitration_id):
                    self.__print_msg(msg)

            actual_waiting_time = time.time() - start_time

        return None

    def __wait_for_addr_claim_multi_collisions_continuous(self, max_wait_time_ms, nmb_collisions):
        """
        Wait max. time for one Address claim requests and simulate address collisions
        :param max_wait_time_ms:
        :param nmb_collisions:
        :return:
        """
        max_time_s = self.__ms_to_seconds(max_wait_time_ms)
        start_time = time.time()
        actual_waiting_time = 0.0

        # Generate can-bus ELD messages for establishing ecm_link connection
        description = "ELD broadcast msgs for Address claim simulation"
        msg_group = ELD_msg_group(description, 10, 600, 10500, 1000, None, None)

        # Needs to be higher priority (= smaller number) than Gen2 NAME (which is based on Serial number): 0x00, 0x00, 0x40, 0x32, 0x00, 0xff, 0x02, 0x10
        data_to_send = [0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03]
        # Needs to send back with the same msg ID to create Address Collision
        max_addr_claim_response_delay_ms = 500  # 250ms request + 250ms response TODO: 250 or 500 ? If works with 250 keep 250ms
        actual_collisions_count = 0

        while actual_waiting_time <= max_time_s:
            # J1939 messages need to be broadcast for Address claim Ehubo2 mechanism
            self.__send_eld_broadcast_mesages(msg_group)

            msg = self.can_bus.wait_for_one_msg(0.05)  # Wait/Read Address request from Ehubo2

            if msg is not None:
                if self.__is_addr_claim_msg(msg.arbitration_id):
                    self.__print_msg(msg)
                    if actual_collisions_count < nmb_collisions:
                        # Generate Address Collision J1939 message and send it into can-bus
                        addr_collision_response = can.Message(arbitration_id=msg.arbitration_id, extended_id=True,
                                                              data=data_to_send)
                        self.__send_one_msg(addr_collision_response, print_msg_flag=True)
                        actual_collisions_count += 1
                    else:
                        pass

            actual_waiting_time = time.time() - start_time

        return actual_collisions_count

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
    def is_VIN_code_request_msg(msg):
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

    @staticmethod
    def is_engine_hours_request_msg(msg):
        """
        Check if 'arbitration_id' from can-bus is 'Engine hours' message ID
        :param msg_id:
        :return:
        """
        assert isinstance(msg, can.Message)
        MSG_ID_MASK = 0x00FF0000
        REQUEST_MSG_ID = 0xEA  # J1939 Request message ID
        ENGINE_HOURS_MSG_ID = 0xFEE5
        requested_msg_id = 0  # J1939 msg ID which is requested from network
        masked_msg_id = (MSG_ID_MASK & msg.arbitration_id) >> 16
        if masked_msg_id == REQUEST_MSG_ID:
            requested_msg_id |= msg.data[2] << 16  # 0x00
            requested_msg_id |= msg.data[1] << 8  # 0xFE
            requested_msg_id |= msg.data[0]  # 0xEC
            return requested_msg_id == ENGINE_HOURS_MSG_ID
        else:
            False

    @staticmethod
    def __is_engine_hours_request_msg(msg):
        """
        Check if 'arbitration_id' from can-bus is 'engine hours request' message ID
        :param msg_id:
        :return:
        """
        assert isinstance(msg, can.Message)
        MSG_ID_MASK = 0x00FF0000
        REQUEST_MSG_ID = 0xEA  # J1939 Request message ID
        ENGINE_HOURS_MSG_ID = 0xFEE5
        requested_msg_id = 0  # J1939 msg ID which is requested from network
        masked_msg_id = (MSG_ID_MASK & msg.arbitration_id) >> 16
        if masked_msg_id == REQUEST_MSG_ID:

            requested_msg_id |= msg.data[2] << 16
            requested_msg_id |= msg.data[1] << 8
            requested_msg_id |= msg.data[0]

            if requested_msg_id == ENGINE_HOURS_MSG_ID:
                return True
            else:
                return False
        else:
            False

    def __wait_for_one_addr_claim(self, max_wait_time_s):
        """
        Wait for one 'Address Claim' request
        :param max_wait_time_s:
        :return:
        """
        start_time = time.time()
        actual_waiting_time = 0.0
        while actual_waiting_time <= max_wait_time_s:
            msg = self.can_bus.wait_for_one_msg(0.05)

            if msg is not None:
                if self.__is_addr_claim_msg(msg.arbitration_id):
                    self.__print_msg(msg)
                    return msg

            actual_waiting_time = time.time() - start_time

        return None

    @staticmethod
    def __ms_to_seconds(ms_time):
        """
        Convert time [ms] to time [s]
        :param ms_time:
        :return:
        """
        return ms_time / 1000.0

    @staticmethod
    def __get_addr_claim_req_msg(msg_arbitration_id):
        """
        Return Address claim request for specific Address
        Address claim ID = EEFFxx + Default Ehubo2 Address is 0xFB (251 dec)
        :param addr: Address which we want to claim
        :return:
        """
        # Data need to have higher priority (= smaller number) than Gen2 NAME: 0x00, 0x00, 0x40, 0x32, 0x00, 0xff, 0x02, 0x10
        data_to_send = [0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03]
        return can.Message(arbitration_id=msg_arbitration_id, extended_id=True, data=data_to_send)

    def __new_device_addr_collisions_multi_continuous(self, max_wait_time_ms, nmb_collisions):
        """
        Simulate new device on can-bus which tries to use the same Address as Ehubo2 address
        - Start with default Ehubo2 address = 0xfb (251)
        - Simulate ELD broadcast messages to re-establish ecm_link connection (Speed, Engine r.p.m., Distance)
        - Generate multiple address claim collisions from new device on can-bus
        - complete on timeout
        :param max_wait_time_ms:
        :param nmb_collisions:
        :return:
        """
        DELAY_FOR_ECM_LINK_S = 2  # provide Ehubo2 time to re-establish ecm_link

        max_time_s = self.__ms_to_seconds(max_wait_time_ms)
        start_time = time.time()
        actual_waiting_time = 0.0

        # Generate can-bus ELD messages for establishing ecm_link connection
        description = "ELD broadcast msgs for Address claim simulation"
        msg_group = ELD_msg_group(description, 10, 600, 10500, 1000, None, None)

        initial_request = True
        actual_collisions_count = 0
        while actual_waiting_time <= max_time_s:

            self.__send_eld_broadcast_mesages(msg_group)    # Broadcast messages required by ELD
            if actual_collisions_count < nmb_collisions:
                if actual_waiting_time > DELAY_FOR_ECM_LINK_S:  # Provide Ehubo2 enough time to re-establish ecm_link
                    if initial_request:
                        # Default Ehubo2 address is 0xfb -> default arbitration_id = 0x18eefffb
                        self.__send_one_msg(self.__get_addr_claim_req_msg(0x18eefffb), print_msg_flag=True)
                        initial_request = False

                    addr_claim_msg = self.__wait_for_one_addr_claim(0.5)

                    if addr_claim_msg is not None:
                        if self.__is_addr_claim_msg(addr_claim_msg.arbitration_id):
                            # Generate next collision here
                            self.__send_one_msg(self.__get_addr_claim_req_msg(addr_claim_msg.arbitration_id),
                                                print_msg_flag=True)
                            actual_collisions_count += 1

                else:
                    time.sleep(0.05)

            else:
                time.sleep(0.05)

            actual_waiting_time = time.time() - start_time

        return actual_collisions_count

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
            self.__send_one_msg(can_frame, print_msg_flag=True)
            time.sleep(0.050)  # According J1939 std. multi frame messages with 50ms time delay

    def __broadcast_and_reply_VIN_multi_frame(self, max_wait_time_ms):
        """
        Broadcast F004 message and response on VIN code request for Install wizard test
        """
        actual_wait_time = 0
        start_time = time.time() * 1000

        while actual_wait_time < max_wait_time_ms:
            rpm_msg = self.get_EEC1_message(2000)
            self.__send_one_msg(rpm_msg, print_msg_flag=True)
            msg = self.__wait_for_VIN_code_request(100)
            actual_wait_time = time.time() * 1000 - start_time

            if msg is None:
                print('No \'VIN code\' request received in {0} seconds'.format(self.__ms_to_seconds(max_wait_time_ms)))
                continue

            # Build and send VIN code message as multi-frame can message
            vin_code_multi_messages = self.__get_VIN_code_multi_frame()
            for can_frame in vin_code_multi_messages:
                self.__send_one_msg(can_frame, print_msg_flag=True)
                time.sleep(0.050)  # According J1939 std. multi frame messages with 50ms time delay

        print("- Simulation for Install wizard completed. -")

    def __eld_simulation_default(self, max_wait_time_ms):
        """
        Perform truck simulation for truck
        - keep sending broadcast messages: Speed, Engine speed, Vehicle distance
        - response on request messages: Engine hours and VIN code
        :param max_wait_time_ms:
        :return:
        """
        description = "Default ELD simulation"
        msg_group = ELD_msg_group(description, 10, 600, 10500, 1000, None, max_wait_time_ms / 1000)
        ccvs = self.get_CCVS1_message(msg_group.vehicle_speed)
        eec1 = self.get_EEC1_message(msg_group.engine_speed)
        vdhr = self.get_VDHR_message(msg_group.vehicle_distance)
        hours = self.get_HOURS_message(msg_group.engine_hours)

        print("\nSimulating: Default ELD messages for {0} seconds\n".format(msg_group.duration))
        msg_group.print()
        print('...\n')

        self.__run_eld_file_simulation(msg_group.duration, ccvs, eec1, vdhr, hours, False)
        print("- Simulation for ELD completed. -")

    def __eld_file_simulation(self, file_name):
        """
        Perform truck simulation for ELD test procedure - simulation specified in text file
        - keep sending broadcast messages: Speed, Engine speed, Vehicle distance
        - response on request messages: Engine hours and VIN code
        :param max_wait_time_ms:
        :return:
        """
        eld_simulation = ELD_simulation(file_name)
        eld_simulation.print_simulation_sequence()

        for msg_group in eld_simulation.msg_group_list:
            # Iterate over all message group
            print("\nSimulating: {0}\n".format(msg_group.description))
            msg_group.print()
            print('...\n')

            ccvs = self.get_CCVS1_message(msg_group.vehicle_speed)
            eec1 = self.get_EEC1_message(msg_group.engine_speed)
            vdhr = self.get_VDHR_message(msg_group.vehicle_distance)
            hours = self.get_HOURS_message(msg_group.engine_hours)

            self.__run_eld_file_simulation(msg_group.duration, ccvs, eec1, vdhr, hours, False)
        print("- Simulation for ELD completed. -")

    def __run_eld_file_simulation(self, max_duration_s, ccvs, eec1, vdhr, hours, print_out_msg_flag=False):
        """
        Simulate J1939 messages for ELD behavior
        :return:
        """
        actual_duration_time = 0
        start_time = time.time()

        # Simulate one message group for specific duration time
        while (time.time() - start_time) < max_duration_s:
            self.__send_one_msg(eec1, print_out_msg_flag)
            self.__send_one_msg(ccvs, print_out_msg_flag)
            self.__send_one_msg(vdhr, print_out_msg_flag)

            msg = self.__wait_for_VIN_or_engine_hours_request(100)

            if msg is None:
                # print('No \'VIN code\' or \'Engine hours\' request received in {0} seconds'.format(
                #     self.__ms_to_seconds(max_wait_time_ms)))
                continue

            if self.is_VIN_code_request_msg(msg):
                # Build and send VIN code message as multi-frame can message
                vin_code_multi_messages = self.__get_VIN_code_multi_frame()
                for can_frame in vin_code_multi_messages:
                    print('VIN code request received - sending response now')
                    self.__send_one_msg(can_frame)
                    time.sleep(0.050)  # According J1939 std. multi frame messages with 50ms time delay

            if self.is_engine_hours_request_msg(msg):
                print('Engine Hours request received - sending response now')
                self.__send_one_msg(hours)

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
            # msg = self.can_bus.get_one_msg()
            msg = self.can_bus.wait_for_one_msg(0.005)

            if msg is not None:
                if self.is_VIN_code_request_msg(msg):
                    self.__print_msg(msg)
                    return msg

            actual_waiting_time = time.time() - start_time

        return None

    def __wait_for_VIN_or_engine_hours_request(self, max_wait_time_ms):
        """
        Wait max. time for one VIN code or Engine Hours request message
        :param max_wait_time_ms:
        :return:
        """
        max_time_s = self.__ms_to_seconds(max_wait_time_ms)
        start_time = time.time()
        actual_waiting_time = 0.0

        while actual_waiting_time <= max_time_s:
            # msg = self.can_bus.get_one_msg()
            msg = self.can_bus.wait_for_one_msg(0.005)

            if msg is not None:
                if self.is_VIN_code_request_msg(msg):
                    self.__print_msg(msg)
                    return msg
                elif self.is_engine_hours_request_msg(msg):
                    self.__print_msg(msg)
                    return msg
                else:
                    pass

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
        msg1_data = [0x01, 53, 71, 90, 67, 90, 52, 51]
        msg1 = can.Message(arbitration_id=0x18EBFF01, extended_id=True, data=msg1_data)
        msg2_data = [0x02, 68, 49, 51, 83, 56, 49, 50]
        msg2 = can.Message(arbitration_id=0x18EBFF01, extended_id=True, data=msg2_data)
        msg3_data = [0x03, 55, 49, 53, 42, 0xFF, 0xFF, 0xFF]
        msg3 = can.Message(arbitration_id=0x18EBFF01, extended_id=True, data=msg3_data)

        return [initial_frame_msg, msg1, msg2, msg3]

    @staticmethod
    def __get_engine_hours_message():
        """
        Generate engine hours message
        :return:
        """
        msg_data = [0x64, 0x05, 0x01, 0x00, 0x1B, 0xF2, 0x03, 0x00]
        engine_hours_msg = can.Message(arbitration_id=0x18FEE501, extended_id=True, data=msg_data)
        return engine_hours_msg

    def __wait_for_engine_hours_request(self, max_wait_time_ms):
        """
        Wait max. time for one engine hours request message
        :param max_wait_time_ms:
        :return:
        """
        max_time_s = self.__ms_to_seconds(max_wait_time_ms)
        start_time = time.time()
        actual_waiting_time = 0.0

        while actual_waiting_time <= max_time_s:
            # msg = self.can_bus.get_one_msg()
            msg = self.can_bus.wait_for_one_msg(0.005)

            if msg is not None:
                if self.is_engine_hours_request_msg(msg):
                    self.__print_msg(msg)
                    return msg

            actual_waiting_time = time.time() - start_time

        return None

    def __wait_and_reply_engine_hours(self, max_wait_time_ms):
        """
        Wait max. time for engine hours request and reply with engine hours message
        :param max_wait_time_ms:
        :return:
        """
        msg = self.__wait_for_engine_hours_request(max_wait_time_ms)

        if msg is None:
            print('No \'Engine hours\' request received in {0} seconds'.format(self.__ms_to_seconds(max_wait_time_ms)))
            return

        # Build and send engine hours message
        self.__send_one_msg(self.__get_engine_hours_message(), print_msg_flag=True)

    def __simulate_rpm_shift(self, rpm_1_value, rpm_1_time_ms, rpm_2_value, rpm_2_time_ms):
        """
        Simulate Engine shift from one RPM value to second RPM value for specified time
        """
        rpm_msg_1 = self.get_EEC1_message(rpm_1_value)  # RPM signal is sent inside EEC1 J1939 message
        rpm_msg_2 = self.get_EEC1_message(rpm_2_value)
        rpm_1_time_s = self.__ms_to_seconds(rpm_1_time_ms)
        rpm_2_time_s = self.__ms_to_seconds(rpm_2_time_ms)

        print('Sending RPM value: {0} for {1} second(s)'.format(rpm_1_value, rpm_1_time_s))
        self.__keep_sending_message_for_max_time(rpm_msg_1, 20, rpm_1_time_ms)  # Cycle time 20ms (see J1939 std.)
        print('Sending RPM value: {0} for {1} second(s)'.format(rpm_2_value, rpm_2_time_s))
        self.__keep_sending_message_for_max_time(rpm_msg_2, 20, rpm_2_time_ms)  # Cycle time 20ms (see J1939 std.)

    def __simulate_speed_shift(self, kph_1_value, speed_1_time_ms, kph_2_value, speed_2_time_ms):
        """
        Simulate Vehicle Speed shift from one kph value to second kph value for specified time [ms]
        """
        kph_msg_1 = self.get_CCVS1_message(kph_1_value)  # Vehicle Speed signal is sent inside CCVS1 J1939 message
        kph_msg_2 = self.get_CCVS1_message(kph_2_value)
        kph_1_time_s = self.__ms_to_seconds(speed_1_time_ms)
        kph_2_time_s = self.__ms_to_seconds(speed_2_time_ms)

        print('Sending Vehicle Speed value: {0} for {1} second(s)'.format(kph_1_value, kph_1_time_s))
        self.__keep_sending_message_for_max_time(kph_msg_1, 100, speed_1_time_ms)  # Cycle time 100ms (see J1939 std.)
        print('Sending Vehicle Speed value: {0} for {1} second(s)'.format(kph_2_value, kph_2_time_s))
        self.__keep_sending_message_for_max_time(kph_msg_2, 100, speed_2_time_ms)  # Cycle time 100ms (see J1939 std.)

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
                self.__send_one_msg(msg_to_send, print_msg_flag=False)
                time.sleep(delay_seconds)
                actual_waiting_time = time.time() - start_time

    def __send_eld_broadcast_mesages(self, msg_group, print_out=False):
        """
        Send broadcast ELD messages
        :param msg_group:
        :return:
        """
        ccvs = self.get_CCVS1_message(msg_group.vehicle_speed)
        eec1 = self.get_EEC1_message(msg_group.engine_speed)
        vdhr = self.get_VDHR_message(msg_group.vehicle_distance)
        self.__send_one_msg(ccvs, print_out)
        self.__send_one_msg(eec1, print_out)
        self.__send_one_msg(vdhr, print_out)

    @staticmethod
    def get_EEC1_message(rpm_value):
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

    @staticmethod
    def get_CCVS1_message(speed_kmh):
        """
        Get J1939 CCVS message with specific vehicle speed value
        :return:
        """
        ccvs_id = 0x18FEF101
        speed_lsb = speed_msb = 0

        try:
            raw_speed_value = int(round(speed_kmh * 256))  # See J1939 std. CCVS message: 1/256 km/h per bit gain
            speed_lsb = raw_speed_value & 0x00FF
            speed_msb = (raw_speed_value & 0xFF00) >> 8
        except ValueError:
            print('Error: Cannot convert physical RPM value into raw value for EEC1 message')
            return None

        ccvs_data = [0x00, speed_lsb, speed_msb, 0x00, 0x00, 0x00, 0x00, 0x00]
        return can.Message(arbitration_id=ccvs_id, extended_id=True, data=ccvs_data)

    @staticmethod
    def get_VDHR_message(vehicle_distance_meters):
        """
        Get J1939 VDHR (Vehicle Distance High Resolution) message with specific distance value (in meters)
        :param vehicle_distance:
        :return:
        """
        vdhr_id = 0x18FEC101
        byte1 = byte2 = byte3 = byte4 = 0  # byte1 = lsb; byte4 = msb

        try:
            raw_distance_value = int(round(vehicle_distance_meters / 5))  # See J1939 std. VDHR message: 5m per bit gain
            byte1 = raw_distance_value & 0x000000FF
            byte2 = (raw_distance_value & 0x0000FF00) >> 8
            byte3 = (raw_distance_value & 0x00FF0000) >> 16
            byte4 = (raw_distance_value & 0xFF000000) >> 24
        except ValueError:
            print('Error: Cannot convert physical RPM value into raw value for EEC1 message')
            return None

        vdhr_data = [byte1, byte2, byte3, byte4, 0x00, 0x00, 0x00, 0x00]
        return can.Message(arbitration_id=vdhr_id, extended_id=True, data=vdhr_data)

    @staticmethod
    def get_HOURS_message(engine_hours):
        """
        Get J1939 Engine Hours message with specific hours value
        :return:
        """
        hours_id = 0x18FEE501
        byte1 = byte2 = byte3 = byte4 = 0  # byte1 = lsb; byte4 = msb

        try:
            raw_hours_value = int(round(engine_hours / 0.05))  # See J1939 std. HOURS message: 0.05 H per bit gain
            byte1 = raw_hours_value & 0x000000FF
            byte2 = (raw_hours_value & 0x0000FF00) >> 8
            byte3 = (raw_hours_value & 0x00FF0000) >> 16
            byte4 = (raw_hours_value & 0xFF000000) >> 24
        except ValueError:
            print('Error: Cannot convert physical RPM value into raw value for EEC1 message')
            return None

        hours_data = [byte1, byte2, byte3, byte4, 0x00, 0x00, 0x00, 0x00]
        return can.Message(arbitration_id=hours_id, extended_id=True, data=hours_data)

    def __print_msg(self, msg, received=True):
        """
        Print message in cmd shell
        '-->' ... means message was received
        '<--' ... means message was sent
        :param msg:
        :param received:
        :return:
        """
        if received:
            print('--> ', msg)
        else:
            print('<-- ', msg)
