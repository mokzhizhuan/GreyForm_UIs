// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from my_robot_wallinterfaces:msg/SelectionWall.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "my_robot_wallinterfaces/msg/detail/selection_wall__rosidl_typesupport_introspection_c.h"
#include "my_robot_wallinterfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "my_robot_wallinterfaces/msg/detail/selection_wall__functions.h"
#include "my_robot_wallinterfaces/msg/detail/selection_wall__struct.h"


// Include directives for member types
// Member `wallselection`
// Member `typeselection`
#include "rosidl_runtime_c/string_functions.h"
// Member `picked_position`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  my_robot_wallinterfaces__msg__SelectionWall__init(message_memory);
}

void my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_fini_function(void * message_memory)
{
  my_robot_wallinterfaces__msg__SelectionWall__fini(message_memory);
}

size_t my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__size_function__SelectionWall__picked_position(
  const void * untyped_member)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return member->size;
}

const void * my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__get_const_function__SelectionWall__picked_position(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void * my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__get_function__SelectionWall__picked_position(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__fetch_function__SelectionWall__picked_position(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int32_t * item =
    ((const int32_t *)
    my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__get_const_function__SelectionWall__picked_position(untyped_member, index));
  int32_t * value =
    (int32_t *)(untyped_value);
  *value = *item;
}

void my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__assign_function__SelectionWall__picked_position(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int32_t * item =
    ((int32_t *)
    my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__get_function__SelectionWall__picked_position(untyped_member, index));
  const int32_t * value =
    (const int32_t *)(untyped_value);
  *item = *value;
}

bool my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__resize_function__SelectionWall__picked_position(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  rosidl_runtime_c__int32__Sequence__fini(member);
  return rosidl_runtime_c__int32__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_message_member_array[4] = {
  {
    "wallselection",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(my_robot_wallinterfaces__msg__SelectionWall, wallselection),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "typeselection",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(my_robot_wallinterfaces__msg__SelectionWall, typeselection),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "sectionselection",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(my_robot_wallinterfaces__msg__SelectionWall, sectionselection),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "picked_position",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(my_robot_wallinterfaces__msg__SelectionWall, picked_position),  // bytes offset in struct
    NULL,  // default value
    my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__size_function__SelectionWall__picked_position,  // size() function pointer
    my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__get_const_function__SelectionWall__picked_position,  // get_const(index) function pointer
    my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__get_function__SelectionWall__picked_position,  // get(index) function pointer
    my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__fetch_function__SelectionWall__picked_position,  // fetch(index, &value) function pointer
    my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__assign_function__SelectionWall__picked_position,  // assign(index, value) function pointer
    my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__resize_function__SelectionWall__picked_position  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_message_members = {
  "my_robot_wallinterfaces__msg",  // message namespace
  "SelectionWall",  // message name
  4,  // number of fields
  sizeof(my_robot_wallinterfaces__msg__SelectionWall),
  my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_message_member_array,  // message members
  my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_init_function,  // function to initialize message memory (memory has to be allocated)
  my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_message_type_support_handle = {
  0,
  &my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_my_robot_wallinterfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, my_robot_wallinterfaces, msg, SelectionWall)() {
  if (!my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_message_type_support_handle.typesupport_identifier) {
    my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &my_robot_wallinterfaces__msg__SelectionWall__rosidl_typesupport_introspection_c__SelectionWall_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
