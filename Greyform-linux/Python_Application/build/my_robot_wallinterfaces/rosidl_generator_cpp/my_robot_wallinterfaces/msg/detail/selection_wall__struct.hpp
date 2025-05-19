// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from my_robot_wallinterfaces:msg/SelectionWall.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__STRUCT_HPP_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__my_robot_wallinterfaces__msg__SelectionWall __attribute__((deprecated))
#else
# define DEPRECATED__my_robot_wallinterfaces__msg__SelectionWall __declspec(deprecated)
#endif

namespace my_robot_wallinterfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct SelectionWall_
{
  using Type = SelectionWall_<ContainerAllocator>;

  explicit SelectionWall_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->wallselection = "";
      this->typeselection = "";
    }
  }

  explicit SelectionWall_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : wallselection(_alloc),
    typeselection(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->wallselection = "";
      this->typeselection = "";
    }
  }

  // field types and members
  using _wallselection_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _wallselection_type wallselection;
  using _typeselection_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _typeselection_type typeselection;
  using _picked_position_type =
    std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>>;
  _picked_position_type picked_position;

  // setters for named parameter idiom
  Type & set__wallselection(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->wallselection = _arg;
    return *this;
  }
  Type & set__typeselection(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->typeselection = _arg;
    return *this;
  }
  Type & set__picked_position(
    const std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>> & _arg)
  {
    this->picked_position = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator> *;
  using ConstRawPtr =
    const my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__my_robot_wallinterfaces__msg__SelectionWall
    std::shared_ptr<my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__my_robot_wallinterfaces__msg__SelectionWall
    std::shared_ptr<my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SelectionWall_ & other) const
  {
    if (this->wallselection != other.wallselection) {
      return false;
    }
    if (this->typeselection != other.typeselection) {
      return false;
    }
    if (this->picked_position != other.picked_position) {
      return false;
    }
    return true;
  }
  bool operator!=(const SelectionWall_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SelectionWall_

// alias to use template instance with default allocator
using SelectionWall =
  my_robot_wallinterfaces::msg::SelectionWall_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace my_robot_wallinterfaces

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__STRUCT_HPP_
