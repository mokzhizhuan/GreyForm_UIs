// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from my_robot_wallinterfaces:msg/FileExtractionMessage.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__BUILDER_HPP_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace my_robot_wallinterfaces
{

namespace msg
{

namespace builder
{

class Init_FileExtractionMessage_status
{
public:
  explicit Init_FileExtractionMessage_status(::my_robot_wallinterfaces::msg::FileExtractionMessage & msg)
  : msg_(msg)
  {}
  ::my_robot_wallinterfaces::msg::FileExtractionMessage status(::my_robot_wallinterfaces::msg::FileExtractionMessage::_status_type arg)
  {
    msg_.status = std::move(arg);
    return std::move(msg_);
  }

private:
  ::my_robot_wallinterfaces::msg::FileExtractionMessage msg_;
};

class Init_FileExtractionMessage_stl_data
{
public:
  explicit Init_FileExtractionMessage_stl_data(::my_robot_wallinterfaces::msg::FileExtractionMessage & msg)
  : msg_(msg)
  {}
  Init_FileExtractionMessage_status stl_data(::my_robot_wallinterfaces::msg::FileExtractionMessage::_stl_data_type arg)
  {
    msg_.stl_data = std::move(arg);
    return Init_FileExtractionMessage_status(msg_);
  }

private:
  ::my_robot_wallinterfaces::msg::FileExtractionMessage msg_;
};

class Init_FileExtractionMessage_excelfile
{
public:
  Init_FileExtractionMessage_excelfile()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_FileExtractionMessage_stl_data excelfile(::my_robot_wallinterfaces::msg::FileExtractionMessage::_excelfile_type arg)
  {
    msg_.excelfile = std::move(arg);
    return Init_FileExtractionMessage_stl_data(msg_);
  }

private:
  ::my_robot_wallinterfaces::msg::FileExtractionMessage msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::my_robot_wallinterfaces::msg::FileExtractionMessage>()
{
  return my_robot_wallinterfaces::msg::builder::Init_FileExtractionMessage_excelfile();
}

}  // namespace my_robot_wallinterfaces

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__BUILDER_HPP_
