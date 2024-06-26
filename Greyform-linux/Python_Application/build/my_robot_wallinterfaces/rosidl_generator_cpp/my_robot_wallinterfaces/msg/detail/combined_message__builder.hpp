// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from my_robot_wallinterfaces:msg/CombinedMessage.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__BUILDER_HPP_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "my_robot_wallinterfaces/msg/detail/combined_message__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace my_robot_wallinterfaces
{

namespace msg
{

namespace builder
{

class Init_CombinedMessage_file_extraction
{
public:
  explicit Init_CombinedMessage_file_extraction(::my_robot_wallinterfaces::msg::CombinedMessage & msg)
  : msg_(msg)
  {}
  ::my_robot_wallinterfaces::msg::CombinedMessage file_extraction(::my_robot_wallinterfaces::msg::CombinedMessage::_file_extraction_type arg)
  {
    msg_.file_extraction = std::move(arg);
    return std::move(msg_);
  }

private:
  ::my_robot_wallinterfaces::msg::CombinedMessage msg_;
};

class Init_CombinedMessage_wall_extraction
{
public:
  Init_CombinedMessage_wall_extraction()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CombinedMessage_file_extraction wall_extraction(::my_robot_wallinterfaces::msg::CombinedMessage::_wall_extraction_type arg)
  {
    msg_.wall_extraction = std::move(arg);
    return Init_CombinedMessage_file_extraction(msg_);
  }

private:
  ::my_robot_wallinterfaces::msg::CombinedMessage msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::my_robot_wallinterfaces::msg::CombinedMessage>()
{
  return my_robot_wallinterfaces::msg::builder::Init_CombinedMessage_wall_extraction();
}

}  // namespace my_robot_wallinterfaces

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__BUILDER_HPP_
