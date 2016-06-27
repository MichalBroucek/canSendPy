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
- Wait for specific can message (timeout)
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
- ...

