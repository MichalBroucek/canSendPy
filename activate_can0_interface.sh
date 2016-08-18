#!/bin/bash

CAN_INTERFACE="can0"

echo -e "Loading 'can_dev' and 'vcan' kernels' modules\n"

sudo modprobe can_dev
sudo modprobe vcan

echo -e "Activating $CAN_INTERFACE interface\n"
sudo ip link set $CAN_INTERFACE type can bitrate 250000
sudo ip link set $CAN_INTERFACE up
# sudo ip link del vcan0

ifconfig $CAN_INTERFACE
echo -e "\n"

