cmake_minimum_required(VERSION 3.8)
project(my_robot_wallinterfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(catkin REQUIRED COMPONENTS
  message_generation
  std_msgs
)

add_message_files(
  FILES
  FileExtractionMessage.msg
  SelectionWall.msg
)

add_service_files(
  FILES
  SetLed.srv
)

# generate added messages and services
generate_messages(
  DEPENDENCIES
  std_msgs
)

# catkin specific configuration
catkin_package(
  CATKIN_DEPENDS message_runtime std_msgs 
)

# specify include directories
include_directories(
  ${catkin_INCLUDE_DIRS}
)
