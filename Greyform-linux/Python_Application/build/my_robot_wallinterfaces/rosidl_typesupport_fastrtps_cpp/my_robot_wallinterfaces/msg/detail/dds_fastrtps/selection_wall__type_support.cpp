// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from my_robot_wallinterfaces:msg/SelectionWall.idl
// generated code does not contain a copyright notice
#include "my_robot_wallinterfaces/msg/detail/selection_wall__rosidl_typesupport_fastrtps_cpp.hpp"
#include "my_robot_wallinterfaces/msg/detail/selection_wall__struct.hpp"

#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions

namespace my_robot_wallinterfaces
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_my_robot_wallinterfaces
cdr_serialize(
  const my_robot_wallinterfaces::msg::SelectionWall & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: wallselection
  cdr << ros_message.wallselection;
  // Member: typeselection
  cdr << ros_message.typeselection;
  // Member: sectionselection
  cdr << ros_message.sectionselection;
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_my_robot_wallinterfaces
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  my_robot_wallinterfaces::msg::SelectionWall & ros_message)
{
  // Member: wallselection
  cdr >> ros_message.wallselection;

  // Member: typeselection
  cdr >> ros_message.typeselection;

  // Member: sectionselection
  cdr >> ros_message.sectionselection;

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_my_robot_wallinterfaces
get_serialized_size(
  const my_robot_wallinterfaces::msg::SelectionWall & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: wallselection
  {
    size_t item_size = sizeof(ros_message.wallselection);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: typeselection
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.typeselection.size() + 1);
  // Member: sectionselection
  {
    size_t item_size = sizeof(ros_message.sectionselection);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_my_robot_wallinterfaces
max_serialized_size_SelectionWall(
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


  // Member: wallselection
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: typeselection
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

  // Member: sectionselection
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = my_robot_wallinterfaces::msg::SelectionWall;
    is_plain =
      (
      offsetof(DataType, sectionselection) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static bool _SelectionWall__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const my_robot_wallinterfaces::msg::SelectionWall *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _SelectionWall__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<my_robot_wallinterfaces::msg::SelectionWall *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _SelectionWall__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const my_robot_wallinterfaces::msg::SelectionWall *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _SelectionWall__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_SelectionWall(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _SelectionWall__callbacks = {
  "my_robot_wallinterfaces::msg",
  "SelectionWall",
  _SelectionWall__cdr_serialize,
  _SelectionWall__cdr_deserialize,
  _SelectionWall__get_serialized_size,
  _SelectionWall__max_serialized_size
};

static rosidl_message_type_support_t _SelectionWall__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_SelectionWall__callbacks,
  get_message_typesupport_handle_function,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace my_robot_wallinterfaces

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_my_robot_wallinterfaces
const rosidl_message_type_support_t *
get_message_type_support_handle<my_robot_wallinterfaces::msg::SelectionWall>()
{
  return &my_robot_wallinterfaces::msg::typesupport_fastrtps_cpp::_SelectionWall__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, my_robot_wallinterfaces, msg, SelectionWall)() {
  return &my_robot_wallinterfaces::msg::typesupport_fastrtps_cpp::_SelectionWall__handle;
}

#ifdef __cplusplus
}
#endif
