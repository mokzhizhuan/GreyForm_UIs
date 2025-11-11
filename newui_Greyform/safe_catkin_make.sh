#!/usr/bin/env bash
set -euo pipefail

WS="/root/catkin_ws/newui_Greyform"
cd "$WS"

# Ensure top-level CMakeLists is correct
if ! grep -q 'toplevel.cmake' "src/CMakeLists.txt" 2>/dev/null; then
  rm -f src/CMakeLists.txt
  catkin_init_workspace src
fi

# Fix bad CMake caches that point to a package dir, without nuking build/
if [ -f build/CMakeCache.txt ] && grep -Eq 'CMAKE_HOME_DIRECTORY:INTERNAL=.*/src/[^/]+/?$' build/CMakeCache.txt; then
  echo "[fix] CMake cache referenced a package — resetting cache files"
  rm -f build/CMakeCache.txt
  rm -rf build/CMakeFiles
fi

# Build
source /opt/ros/noetic/setup.bash
catkin_make

# Source the overlay so subsequent commands in this shell have your packages
if [ -f devel/setup.bash ]; then
  source devel/setup.bash
fi

# (Optional) Export a reusable env snapshot for other processes (FastAPI)
# This captures the key variables so your API can start ROS nodes with the correct overlay.
ENV_OUT=".env_after_build"
{
  echo "export ROS_WORKSPACE='$WS'"
  echo "source /opt/ros/noetic/setup.bash"
  if [ -f "$WS/devel/setup.bash" ]; then
    echo "source '$WS/devel/setup.bash'"
  fi
  # You can pin master if you want:
  echo "export ROS_MASTER_URI='http://localhost:11311'"
  echo "export ROS_IP='127.0.0.1'"
} > "$ENV_OUT"

echo "[safe] build complete; overlay sourced. Env snapshot: $WS/$ENV_OUT"
