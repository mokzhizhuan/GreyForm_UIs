// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from my_robot_wallinterfaces:msg/SelectionWall.idl
// generated code does not contain a copyright notice
#include "my_robot_wallinterfaces/msg/detail/selection_wall__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "my_robot_wallinterfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "my_robot_wallinterfaces/msg/detail/selection_wall__struct.h"
#include "my_robot_wallinterfaces/msg/detail/selection_wall__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "rosidl_runtime_c/primitives_sequence.h"  // picked_position
#include "rosidl_runtime_c/primitives_sequence_functions.h"  // picked_position
#include "rosidl_runtime_c/string.h"  // typeselection, wallselection
#include "rosidl_runtime_c/string_functions.h"  // typeselection, wallselection

// forward declare type support functions


using _SelectionWall__ros_msg_type = my_robot_wallinterfaces__msg__SelectionWall;

static bool _SelectionWall__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _SelectionWall__ros_msg_type * ros_message = static_cast<const _SelectionWall__ros_msg_type *>(untyped_ros_message);
  // Field name: wallselection
  {
    const rosidl_runtime_c__String * str = &ros_message->wallselection;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: typeselection
  {
    const rosidl_runtime_c__String * str = &ros_message->typeselection;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: sectionselection
  {
    cdr << ros_message->sectionselection;
  }

  // Field name: picked_position
  {
    size_t size = ros_message->picked_position.size;
    auto array_ptr = ros_message->picked_position.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  return true;
}

static bool _SelectionWall__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _SelectionWall__ros_msg_type * ros_message = static_cast<_SelectionWall__ros_msg_type *>(untyped_ros_message);
  // Field name: wallselection
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->wallselection.data) {
      rosidl_runtime_c__String__init(&ros_message->wallselection);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->wallselection,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'wallselection'\n");
      return false;
    }
  }

  // Field name: typeselection
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->typeselection.data) {
      rosidl_runtime_c__String__init(&ros_message->typeselection);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->typeselection,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'typeselection'\n");
      return false;
    }
  }

  // Field name: sectionselection
  {
    cdr >> ros_message->sectionselection;
  }

  // Field name: picked_position
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->picked_position.data) {
      rosidl_runtime_c__int32__Sequence__fini(&ros_message->picked_position);
    }
    if (!rosidl_runtime_c__int32__Sequence__init(&ros_message->picked_position, size)) {
      fprintf(stderr, "failed to create array for field 'picked_position'");
      return false;
    }
    auto array_ptr = ros_message->picked_position.data;
    cdr.deserializeArray(array_ptr, size);
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_my_robot_wallinterfaces
size_t get_serialized_size_my_robot_wallinterfaces__msg__SelectionWall(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _SelectionWall__ros_msg_type * ros_message = static_cast<const _SelectionWall__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name wallselection
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->wallselection.size + 1);
  // field.name typeselection
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->typeselection.size + 1);
  // field.name sectionselection
  {
    size_t item_size = sizeof(ros_message->sectionselection);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name picked_position
  {
    size_t array_size = ros_message->picked_position.size;
    auto array_ptr = ros_message->picked_position.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _SelectionWall__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_my_robot_wallinterfaces__msg__SelectionWall(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_my_robot_wallinterfaces
size_t max_serialized_size_my_robot_wallinterfaces__msg__SelectionWall(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // member: wallselection
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // member: typeselection
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // member: sectionselection
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: picked_position
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = my_robot_wallinterfaces__msg__SelectionWall;
    is_plain =
      (
      offsetof(DataType, picked_position) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _SelectionWall__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_my_robot_wallinterfaces__msg__SelectionWall(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_SelectionWall = {
  "my_robot_wallinterfaces::msg",
  "SelectionWall",
  _SelectionWall__cdr_serialize,
  _SelectionWall__cdr_deserialize,
  _SelectionWall__get_serialized_size,
  _SelectionWall__max_serialized_size
};

static rosidl_message_type_support_t _SelectionWall__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_SelectionWall,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, my_robot_wallinterfaces, msg, SelectionWall)() {
  return &_SelectionWall__type_support;
}

#if defined(__cplusplus)
}
#endif
