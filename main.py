#!/usr/bin/env python3

from can_msg import CanMsg
#from cansend.can_driver import Can_driver
from can_driver import Can_driver

# def build_can_frame(can_id, data):
#     can_dlc = len(data)
#     data = data.ljust(8, b'\x00')
#     return struct.pack(can_frame_fmt, can_id, can_dlc, data)


# def dissect_can_frame(frame):
#     can_id, can_dlc, data = struct.unpack(can_frame_fmt, frame)
#     return (can_id, can_dlc, data[:can_dlc])

if __name__ == "__main__":
    print("--- cansend ---\n")
    can_interface = 'vcan0'

    # TODO:
    # 1. Parse command line parameters
    # 2. Call appropriate action
    # 3. Generate output cmd, file, ...

    can_handler = Can_driver(can_interface)
    can_handler.activate_socket()

    # Receiving 5 CAN messages
    # for i in range(5):
    #     can_handler.wait_for_one_msg()

    # Sending 5 CAN messages
    # msg_id=0, source_addr=0, msg_dlc=0, msg_data=[]
    data_to_send = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
    msg_to_send = CanMsg(0xFEF1, 0x02, 8, data_to_send)
    for i in range(5):
        can_handler.send_one_msg(msg_to_send)

    # create a raw socket and bind it to the given CAN interface
    # s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    # s.bind((can_interface,))
    #
    # while True:
    #     cf, addr = s.recvfrom(16)
    #
    #     print('Received: can_id=%x, can_dlc=%x, data=%s' % dissect_can_frame(cf))
    #
    #     try:
    #         s.send(cf)
    #     except socket.error:
    #         print('Error sending CAN frame')
    #
    #     try:
    #         s.send(build_can_frame(0x01, b'\x01\x02\x03'))
    #     except socket.error:
    #         print('Error sending CAN frame')

print("Done")
