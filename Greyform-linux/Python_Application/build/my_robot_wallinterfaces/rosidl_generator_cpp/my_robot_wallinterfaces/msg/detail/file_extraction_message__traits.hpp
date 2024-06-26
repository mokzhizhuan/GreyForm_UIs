// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from my_robot_wallinterfaces:msg/FileExtractionMessage.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__TRAITS_HPP_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace my_robot_wallinterfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const FileExtractionMessage & msg,
  std::ostream & out)
{
  out << "{";
  // member: excelfile
  {
    out << "excelfile: ";
    rosidl_generator_traits::value_to_yaml(msg.excelfile, out);
    out << ", ";
  }

  // member: stl_data
  {
    if (msg.stl_data.size() == 0) {
      out << "stl_data: []";
    } else {
      out << "stl_data: [";
      size_t pending_items = msg.stl_data.size();
      for (auto item : msg.stl_data) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const FileExtractionMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: excelfile
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "excelfile: ";
    rosidl_generator_traits::value_to_yaml(msg.excelfile, out);
    out << "\n";
  }

  // member: stl_data
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.stl_data.size() == 0) {
      out << "stl_data: []\n";
    } else {
      out << "stl_data:\n";
      for (auto item : msg.stl_data) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const FileExtractionMessage & msg, bool use_flow_style = false)
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
  const my_robot_wallinterfaces::msg::FileExtractionMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  my_robot_wallinterfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use my_robot_wallinterfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const my_robot_wallinterfaces::msg::FileExtractionMessage & msg)
{
  return my_robot_wallinterfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<my_robot_wallinterfaces::msg::FileExtractionMessage>()
{
  return "my_robot_wallinterfaces::msg::FileExtractionMessage";
}

template<>
inline const char * name<my_robot_wallinterfaces::msg::FileExtractionMessage>()
{
  return "my_robot_wallinterfaces/msg/FileExtractionMessage";
}

template<>
struct has_fixed_size<my_robot_wallinterfaces::msg::FileExtractionMessage>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<my_robot_wallinterfaces::msg::FileExtractionMessage>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<my_robot_wallinterfaces::msg::FileExtractionMessage>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__TRAITS_HPP_
