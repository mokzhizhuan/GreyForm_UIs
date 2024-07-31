// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from my_robot_wallinterfaces:msg/SelectionWall.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__TRAITS_HPP_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "my_robot_wallinterfaces/msg/detail/selection_wall__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace my_robot_wallinterfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const SelectionWall & msg,
  std::ostream & out)
{
  out << "{";
  // member: wallselection
  {
    out << "wallselection: ";
    rosidl_generator_traits::value_to_yaml(msg.wallselection, out);
    out << ", ";
  }

  // member: typeselection
  {
    out << "typeselection: ";
    rosidl_generator_traits::value_to_yaml(msg.typeselection, out);
    out << ", ";
  }

  // member: sectionselection
  {
    out << "sectionselection: ";
    rosidl_generator_traits::value_to_yaml(msg.sectionselection, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SelectionWall & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: wallselection
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "wallselection: ";
    rosidl_generator_traits::value_to_yaml(msg.wallselection, out);
    out << "\n";
  }

  // member: typeselection
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "typeselection: ";
    rosidl_generator_traits::value_to_yaml(msg.typeselection, out);
    out << "\n";
  }

  // member: sectionselection
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "sectionselection: ";
    rosidl_generator_traits::value_to_yaml(msg.sectionselection, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SelectionWall & msg, bool use_flow_style = false)
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
  const my_robot_wallinterfaces::msg::SelectionWall & msg,
  std::ostream & out, size_t indentation = 0)
{
  my_robot_wallinterfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use my_robot_wallinterfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const my_robot_wallinterfaces::msg::SelectionWall & msg)
{
  return my_robot_wallinterfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<my_robot_wallinterfaces::msg::SelectionWall>()
{
  return "my_robot_wallinterfaces::msg::SelectionWall";
}

template<>
inline const char * name<my_robot_wallinterfaces::msg::SelectionWall>()
{
  return "my_robot_wallinterfaces/msg/SelectionWall";
}

template<>
struct has_fixed_size<my_robot_wallinterfaces::msg::SelectionWall>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<my_robot_wallinterfaces::msg::SelectionWall>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<my_robot_wallinterfaces::msg::SelectionWall>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__TRAITS_HPP_
