
import can
import time

can_interface = 'vcan0'
bus = can.interface.Bus(can_interface, bustype='socketcan_native')

# Receive 10 messages
# for i in range(10):
#     message = bus.recv()
#     print(message)


# Non-blocking receiving - timeout
# bus.recv(0.0) ... the read will be executed as non-blocking
# message = bus.recv(1.0)  # Timeout in seconds.
#
# if message is None:
#     print('Timeout occurred, no message.')


# Generating messages
bustype = 'socketcan_native'
channel = 'vcan0'

def producer(id):
    """:param id: Spam the bus with messages including the data id."""
    bus = can.interface.Bus(channel=channel, bustype=bustype)
    for i in range(10):
        msg = can.Message(arbitration_id=0x18FEF102, data=[1, 2, 3, 4, 5, 6, 7, 8], extended_id=True)
        bus.send(msg)
    # Issue #3: Need to keep running to ensure the writing threads stay alive. ?
    time.sleep(1)

producer(10)
