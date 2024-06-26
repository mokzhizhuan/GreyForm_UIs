// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from my_robot_wallinterfaces:msg/CombinedMessage.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "my_robot_wallinterfaces/msg/detail/combined_message__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace my_robot_wallinterfaces
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void CombinedMessage_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) my_robot_wallinterfaces::msg::CombinedMessage(_init);
}

void CombinedMessage_fini_function(void * message_memory)
{
  auto typed_message = static_cast<my_robot_wallinterfaces::msg::CombinedMessage *>(message_memory);
  typed_message->~CombinedMessage();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember CombinedMessage_message_member_array[2] = {
  {
    "wall_extraction",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<my_robot_wallinterfaces::msg::SelectionWall>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(my_robot_wallinterfaces::msg::CombinedMessage, wall_extraction),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "file_extraction",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<my_robot_wallinterfaces::msg::FileExtractionMessage>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(my_robot_wallinterfaces::msg::CombinedMessage, file_extraction),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers CombinedMessage_message_members = {
  "my_robot_wallinterfaces::msg",  // message namespace
  "CombinedMessage",  // message name
  2,  // number of fields
  sizeof(my_robot_wallinterfaces::msg::CombinedMessage),
  CombinedMessage_message_member_array,  // message members
  CombinedMessage_init_function,  // function to initialize message memory (memory has to be allocated)
  CombinedMessage_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t CombinedMessage_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &CombinedMessage_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace my_robot_wallinterfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<my_robot_wallinterfaces::msg::CombinedMessage>()
{
  return &::my_robot_wallinterfaces::msg::rosidl_typesupport_introspection_cpp::CombinedMessage_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, my_robot_wallinterfaces, msg, CombinedMessage)() {
  return &::my_robot_wallinterfaces::msg::rosidl_typesupport_introspection_cpp::CombinedMessage_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
