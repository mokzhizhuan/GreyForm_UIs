// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from my_robot_wallinterfaces:msg/FileExtractionMessage.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__STRUCT_HPP_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__my_robot_wallinterfaces__msg__FileExtractionMessage __attribute__((deprecated))
#else
# define DEPRECATED__my_robot_wallinterfaces__msg__FileExtractionMessage __declspec(deprecated)
#endif

namespace my_robot_wallinterfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct FileExtractionMessage_
{
  using Type = FileExtractionMessage_<ContainerAllocator>;

  explicit FileExtractionMessage_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->excelfile = "";
    }
  }

  explicit FileExtractionMessage_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : excelfile(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->excelfile = "";
    }
  }

  // field types and members
  using _excelfile_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _excelfile_type excelfile;
  using _stl_data_type =
    std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>>;
  _stl_data_type stl_data;

  // setters for named parameter idiom
  Type & set__excelfile(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->excelfile = _arg;
    return *this;
  }
  Type & set__stl_data(
    const std::vector<uint8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<uint8_t>> & _arg)
  {
    this->stl_data = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator> *;
  using ConstRawPtr =
    const my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__my_robot_wallinterfaces__msg__FileExtractionMessage
    std::shared_ptr<my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__my_robot_wallinterfaces__msg__FileExtractionMessage
    std::shared_ptr<my_robot_wallinterfaces::msg::FileExtractionMessage_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const FileExtractionMessage_ & other) const
  {
    if (this->excelfile != other.excelfile) {
      return false;
    }
    if (this->stl_data != other.stl_data) {
      return false;
    }
    return true;
  }
  bool operator!=(const FileExtractionMessage_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct FileExtractionMessage_

// alias to use template instance with default allocator
using FileExtractionMessage =
  my_robot_wallinterfaces::msg::FileExtractionMessage_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace my_robot_wallinterfaces

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__STRUCT_HPP_
