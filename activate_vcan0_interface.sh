#!/bin/bash

CAN_INTERFACE=vcan0

echo -e "Loading 'can_dev' and 'vcan' kernels' modules\n"

sudo modprobe can_dev
sudo modprobe vcan

echo -e "Activating $CAN_INTERFACE interface\n"
sudo ip link add type vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
# sudo ip link del vcan0

ifconfig $CAN_INTERFACE
echo -e "\n"

