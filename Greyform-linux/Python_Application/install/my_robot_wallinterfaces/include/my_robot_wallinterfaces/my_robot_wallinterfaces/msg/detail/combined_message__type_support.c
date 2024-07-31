// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from my_robot_wallinterfaces:msg/CombinedMessage.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "my_robot_wallinterfaces/msg/detail/combined_message__rosidl_typesupport_introspection_c.h"
#include "my_robot_wallinterfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "my_robot_wallinterfaces/msg/detail/combined_message__functions.h"
#include "my_robot_wallinterfaces/msg/detail/combined_message__struct.h"


// Include directives for member types
// Member `wall_extraction`
#include "my_robot_wallinterfaces/msg/selection_wall.h"
// Member `wall_extraction`
#include "my_robot_wallinterfaces/msg/detail/selection_wall__rosidl_typesupport_introspection_c.h"
// Member `file_extraction`
#include "my_robot_wallinterfaces/msg/file_extraction_message.h"
// Member `file_extraction`
#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  my_robot_wallinterfaces__msg__CombinedMessage__init(message_memory);
}

void my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_fini_function(void * message_memory)
{
  my_robot_wallinterfaces__msg__CombinedMessage__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_message_member_array[2] = {
  {
    "wall_extraction",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(my_robot_wallinterfaces__msg__CombinedMessage, wall_extraction),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "file_extraction",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(my_robot_wallinterfaces__msg__CombinedMessage, file_extraction),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_message_members = {
  "my_robot_wallinterfaces__msg",  // message namespace
  "CombinedMessage",  // message name
  2,  // number of fields
  sizeof(my_robot_wallinterfaces__msg__CombinedMessage),
  my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_message_member_array,  // message members
  my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_init_function,  // function to initialize message memory (memory has to be allocated)
  my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_message_type_support_handle = {
  0,
  &my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_my_robot_wallinterfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, my_robot_wallinterfaces, msg, CombinedMessage)() {
  my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, my_robot_wallinterfaces, msg, SelectionWall)();
  my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, my_robot_wallinterfaces, msg, FileExtractionMessage)();
  if (!my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_message_type_support_handle.typesupport_identifier) {
    my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &my_robot_wallinterfaces__msg__CombinedMessage__rosidl_typesupport_introspection_c__CombinedMessage_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
