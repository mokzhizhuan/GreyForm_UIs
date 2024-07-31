// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from my_robot_wallinterfaces:msg/FileExtractionMessage.idl
// generated code does not contain a copyright notice
#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "my_robot_wallinterfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__struct.h"
#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__functions.h"
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

#include "rosidl_runtime_c/primitives_sequence.h"  // stl_data
#include "rosidl_runtime_c/primitives_sequence_functions.h"  // stl_data
#include "rosidl_runtime_c/string.h"  // excelfile, status
#include "rosidl_runtime_c/string_functions.h"  // excelfile, status

// forward declare type support functions


using _FileExtractionMessage__ros_msg_type = my_robot_wallinterfaces__msg__FileExtractionMessage;

static bool _FileExtractionMessage__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _FileExtractionMessage__ros_msg_type * ros_message = static_cast<const _FileExtractionMessage__ros_msg_type *>(untyped_ros_message);
  // Field name: excelfile
  {
    const rosidl_runtime_c__String * str = &ros_message->excelfile;
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

  // Field name: stl_data
  {
    size_t size = ros_message->stl_data.size;
    auto array_ptr = ros_message->stl_data.data;
    cdr << static_cast<uint32_t>(size);
    cdr.serializeArray(array_ptr, size);
  }

  // Field name: status
  {
    const rosidl_runtime_c__String * str = &ros_message->status;
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

  return true;
}

static bool _FileExtractionMessage__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _FileExtractionMessage__ros_msg_type * ros_message = static_cast<_FileExtractionMessage__ros_msg_type *>(untyped_ros_message);
  // Field name: excelfile
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->excelfile.data) {
      rosidl_runtime_c__String__init(&ros_message->excelfile);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->excelfile,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'excelfile'\n");
      return false;
    }
  }

  // Field name: stl_data
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->stl_data.data) {
      rosidl_runtime_c__uint8__Sequence__fini(&ros_message->stl_data);
    }
    if (!rosidl_runtime_c__uint8__Sequence__init(&ros_message->stl_data, size)) {
      fprintf(stderr, "failed to create array for field 'stl_data'");
      return false;
    }
    auto array_ptr = ros_message->stl_data.data;
    cdr.deserializeArray(array_ptr, size);
  }

  // Field name: status
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->status.data) {
      rosidl_runtime_c__String__init(&ros_message->status);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->status,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'status'\n");
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_my_robot_wallinterfaces
size_t get_serialized_size_my_robot_wallinterfaces__msg__FileExtractionMessage(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _FileExtractionMessage__ros_msg_type * ros_message = static_cast<const _FileExtractionMessage__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name excelfile
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->excelfile.size + 1);
  // field.name stl_data
  {
    size_t array_size = ros_message->stl_data.size;
    auto array_ptr = ros_message->stl_data.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name status
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->status.size + 1);

  return current_alignment - initial_alignment;
}

static uint32_t _FileExtractionMessage__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_my_robot_wallinterfaces__msg__FileExtractionMessage(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_my_robot_wallinterfaces
size_t max_serialized_size_my_robot_wallinterfaces__msg__FileExtractionMessage(
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

  // member: excelfile
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
  // member: stl_data
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: status
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

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = my_robot_wallinterfaces__msg__FileExtractionMessage;
    is_plain =
      (
      offsetof(DataType, status) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _FileExtractionMessage__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_my_robot_wallinterfaces__msg__FileExtractionMessage(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_FileExtractionMessage = {
  "my_robot_wallinterfaces::msg",
  "FileExtractionMessage",
  _FileExtractionMessage__cdr_serialize,
  _FileExtractionMessage__cdr_deserialize,
  _FileExtractionMessage__get_serialized_size,
  _FileExtractionMessage__max_serialized_size
};

static rosidl_message_type_support_t _FileExtractionMessage__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_FileExtractionMessage,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, my_robot_wallinterfaces, msg, FileExtractionMessage)() {
  return &_FileExtractionMessage__type_support;
}

#if defined(__cplusplus)
}
#endif
