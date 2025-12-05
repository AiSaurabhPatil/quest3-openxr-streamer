#!/bin/bash

# Isaac Sim Teleop Launcher with VPN DDS Configuration

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
ISAAC_SIM_PATH="/home/saurabh/isaac_sim"

# ============================================
# CRITICAL FOR VPN: Configure FastRTPS peer discovery
# ============================================
# This tells ROS 2 where to find peers on VPN (no multicast)
export FASTRTPS_DEFAULT_PROFILES_FILE=$SCRIPT_DIR/fastdds_vpn.xml

# Set environment variables for Isaac Sim internal ROS 2 Bridge
export ROS_DISTRO=humble
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=0

# Adjust library path
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ISAAC_SIM_PATH/exts/isaacsim.ros2.bridge/humble/lib

echo "============================================"
echo "Starting Isaac Sim Teleop"
echo "============================================"
echo "ROS_DISTRO: $ROS_DISTRO"
echo "RMW_IMPLEMENTATION: $RMW_IMPLEMENTATION"
echo "FASTRTPS_DEFAULT_PROFILES_FILE: $FASTRTPS_DEFAULT_PROFILES_FILE"
echo ""
echo "IMPORTANT: Make sure fastdds_vpn.xml has correct VPN IPs!"
echo "============================================"

$ISAAC_SIM_PATH/python.sh $SCRIPT_DIR/isaac_teleop.py
