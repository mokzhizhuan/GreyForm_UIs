// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from my_robot_wallinterfaces:msg/CombinedMessage.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__TRAITS_HPP_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "my_robot_wallinterfaces/msg/detail/combined_message__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'wall_extraction'
#include "my_robot_wallinterfaces/msg/detail/selection_wall__traits.hpp"
// Member 'file_extraction'
#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__traits.hpp"

namespace my_robot_wallinterfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const CombinedMessage & msg,
  std::ostream & out)
{
  out << "{";
  // member: wall_extraction
  {
    out << "wall_extraction: ";
    to_flow_style_yaml(msg.wall_extraction, out);
    out << ", ";
  }

  // member: file_extraction
  {
    out << "file_extraction: ";
    to_flow_style_yaml(msg.file_extraction, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CombinedMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: wall_extraction
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "wall_extraction:\n";
    to_block_style_yaml(msg.wall_extraction, out, indentation + 2);
  }

  // member: file_extraction
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "file_extraction:\n";
    to_block_style_yaml(msg.file_extraction, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CombinedMessage & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace my_robot_wallinterfaces

namespace rosidl_generator_traits
{

[[deprecated("use my_robot_wallinterfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const my_robot_wallinterfaces::msg::CombinedMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  my_robot_wallinterfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use my_robot_wallinterfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const my_robot_wallinterfaces::msg::CombinedMessage & msg)
{
  return my_robot_wallinterfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<my_robot_wallinterfaces::msg::CombinedMessage>()
{
  return "my_robot_wallinterfaces::msg::CombinedMessage";
}

template<>
inline const char * name<my_robot_wallinterfaces::msg::CombinedMessage>()
{
  return "my_robot_wallinterfaces/msg/CombinedMessage";
}

template<>
struct has_fixed_size<my_robot_wallinterfaces::msg::CombinedMessage>
  : std::integral_constant<bool, has_fixed_size<my_robot_wallinterfaces::msg::FileExtractionMessage>::value && has_fixed_size<my_robot_wallinterfaces::msg::SelectionWall>::value> {};

template<>
struct has_bounded_size<my_robot_wallinterfaces::msg::CombinedMessage>
  : std::integral_constant<bool, has_bounded_size<my_robot_wallinterfaces::msg::FileExtractionMessage>::value && has_bounded_size<my_robot_wallinterfaces::msg::SelectionWall>::value> {};

template<>
struct is_message<my_robot_wallinterfaces::msg::CombinedMessage>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__TRAITS_HPP_
