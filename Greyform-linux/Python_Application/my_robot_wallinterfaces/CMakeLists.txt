cmake_minimum_required(VERSION 3.8)
project(my_robot_wallinterfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/FileExtractionMessage.msg"
  "msg/SelectionWall.msg"
  "srv/SetLed.srv"
  DEPENDENCIES builtin_interfaces
)

ament_package()
