canSendPy
====================

CAN-bus simulation command line tool
--------------------

Python3.5+ cmd tool for Linux to simulate specific can-bus behaviors as specified in J1939.

Requirement
- Working Socket can interface
- HW to communicate on can-bus (or virtual can interface)
- python-can module (sudo python3.5 -m pip install python-can)


*Functionality*
- Read one can message (timeout)
- Read multiple can messages (timeout)
- Send one can message
- Send one message multiple times
- Send messages from text file
- Wait for Address Claim request - no collision
- Wait for Address Claim request - multiple collision
- Wait for new device Address Claim - multiple collision
- Wait for VIN code request - VIN code single frame response
- Wait for VIN code request - VIN code multiple frame response
- Simulate Engine RPM shift from one value to another value
- Changing can-bus baud rate (requires root access)

