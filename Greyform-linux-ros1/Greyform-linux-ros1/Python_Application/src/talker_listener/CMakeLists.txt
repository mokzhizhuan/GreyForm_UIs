cmake_minimum_required(VERSION 3.0.2)
project(talker_listener)

## Find catkin macros and libraries
find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  message_generation
  my_robot_wallinterfaces
)

## Catkin specific configuration
catkin_package(
  CATKIN_DEPENDS rospy std_msgs message_runtime my_robot_wallinterfaces
)


install(PROGRAMS
  talker_listener/talker_node.py
  talker_listener/listener_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

## Specify additional locations of header files
include_directories(
  ${catkin_INCLUDE_DIRS}
)
