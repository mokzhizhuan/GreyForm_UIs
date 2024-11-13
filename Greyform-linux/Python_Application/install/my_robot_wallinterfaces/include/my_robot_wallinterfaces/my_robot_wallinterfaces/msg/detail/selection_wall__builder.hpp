// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from my_robot_wallinterfaces:msg/SelectionWall.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__BUILDER_HPP_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "my_robot_wallinterfaces/msg/detail/selection_wall__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace my_robot_wallinterfaces
{

namespace msg
{

namespace builder
{

class Init_SelectionWall_picked_position
{
public:
  explicit Init_SelectionWall_picked_position(::my_robot_wallinterfaces::msg::SelectionWall & msg)
  : msg_(msg)
  {}
  ::my_robot_wallinterfaces::msg::SelectionWall picked_position(::my_robot_wallinterfaces::msg::SelectionWall::_picked_position_type arg)
  {
    msg_.picked_position = std::move(arg);
    return std::move(msg_);
  }

private:
  ::my_robot_wallinterfaces::msg::SelectionWall msg_;
};

class Init_SelectionWall_sectionselection
{
public:
  explicit Init_SelectionWall_sectionselection(::my_robot_wallinterfaces::msg::SelectionWall & msg)
  : msg_(msg)
  {}
  Init_SelectionWall_picked_position sectionselection(::my_robot_wallinterfaces::msg::SelectionWall::_sectionselection_type arg)
  {
    msg_.sectionselection = std::move(arg);
    return Init_SelectionWall_picked_position(msg_);
  }

private:
  ::my_robot_wallinterfaces::msg::SelectionWall msg_;
};

class Init_SelectionWall_typeselection
{
public:
  explicit Init_SelectionWall_typeselection(::my_robot_wallinterfaces::msg::SelectionWall & msg)
  : msg_(msg)
  {}
  Init_SelectionWall_sectionselection typeselection(::my_robot_wallinterfaces::msg::SelectionWall::_typeselection_type arg)
  {
    msg_.typeselection = std::move(arg);
    return Init_SelectionWall_sectionselection(msg_);
  }

private:
  ::my_robot_wallinterfaces::msg::SelectionWall msg_;
};

class Init_SelectionWall_wallselection
{
public:
  Init_SelectionWall_wallselection()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SelectionWall_typeselection wallselection(::my_robot_wallinterfaces::msg::SelectionWall::_wallselection_type arg)
  {
    msg_.wallselection = std::move(arg);
    return Init_SelectionWall_typeselection(msg_);
  }

private:
  ::my_robot_wallinterfaces::msg::SelectionWall msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::my_robot_wallinterfaces::msg::SelectionWall>()
{
  return my_robot_wallinterfaces::msg::builder::Init_SelectionWall_wallselection();
}

}  // namespace my_robot_wallinterfaces

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__BUILDER_HPP_
