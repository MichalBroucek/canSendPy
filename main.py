#!/usr/bin/env python3

#!/usr/bin/env python3.5

from can_driver import Can_driver

if __name__ == "__main__":
    print("--- cansend ---\n")
    can_interface = 'vcan0'

    # TODO:
    # 1. Parse command line parameters
    # 2. Call appropriate action
    # 3. Generate output cmd, file, ...

    can_handler = Can_driver(can_interface)

    # Sending 5 messages
    # for i in range(5):
    #     can_handler.send_one_msg(None)

    # Receiving 5 messages
    for i in range(5):
        can_handler.wait_for_one_msg()

print("Done")
