// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from my_robot_wallinterfaces:msg/CombinedMessage.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__STRUCT_HPP_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'wall_extraction'
#include "my_robot_wallinterfaces/msg/detail/selection_wall__struct.hpp"
// Member 'file_extraction'
#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__my_robot_wallinterfaces__msg__CombinedMessage __attribute__((deprecated))
#else
# define DEPRECATED__my_robot_wallinterfaces__msg__CombinedMessage __declspec(deprecated)
#endif

namespace my_robot_wallinterfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct CombinedMessage_
{
  using Type = CombinedMessage_<ContainerAllocator>;

  explicit CombinedMessage_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : wall_extraction(_init),
    file_extraction(_init)
  {
    (void)_init;
  }

  explicit CombinedMessage_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : wall_extraction(_alloc, _init),
    file_extraction(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _wall_extraction_type =
    my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator>;
  _wall_extraction_type wall_extraction;
  using _file_extraction_type =
    my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator>;
  _file_extraction_type file_extraction;

  // setters for named parameter idiom
  Type & set__wall_extraction(
    const my_robot_wallinterfaces::msg::SelectionWall_<ContainerAllocator> & _arg)
  {
    this->wall_extraction = _arg;
    return *this;
  }
  Type & set__file_extraction(
    const my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator> & _arg)
  {
    this->file_extraction = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator> *;
  using ConstRawPtr =
    const my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__my_robot_wallinterfaces__msg__CombinedMessage
    std::shared_ptr<my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__my_robot_wallinterfaces__msg__CombinedMessage
    std::shared_ptr<my_robot_wallinterfaces::msg::CombinedMessage_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CombinedMessage_ & other) const
  {
    if (this->wall_extraction != other.wall_extraction) {
      return false;
    }
    if (this->file_extraction != other.file_extraction) {
      return false;
    }
    return true;
  }
  bool operator!=(const CombinedMessage_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CombinedMessage_

// alias to use template instance with default allocator
using CombinedMessage =
  my_robot_wallinterfaces::msg::CombinedMessage_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace my_robot_wallinterfaces

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__STRUCT_HPP_
