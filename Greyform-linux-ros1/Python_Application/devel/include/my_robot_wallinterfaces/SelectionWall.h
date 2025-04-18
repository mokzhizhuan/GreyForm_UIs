// Generated by gencpp from file my_robot_wallinterfaces/SelectionWall.msg
// DO NOT EDIT!


#ifndef MY_ROBOT_WALLINTERFACES_MESSAGE_SELECTIONWALL_H
#define MY_ROBOT_WALLINTERFACES_MESSAGE_SELECTIONWALL_H


#include <string>
#include <vector>
#include <memory>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>


namespace my_robot_wallinterfaces
{
template <class ContainerAllocator>
struct SelectionWall_
{
  typedef SelectionWall_<ContainerAllocator> Type;

  SelectionWall_()
    : wallselection()
    , typeselection()
    , picked_position()  {
    }
  SelectionWall_(const ContainerAllocator& _alloc)
    : wallselection(_alloc)
    , typeselection(_alloc)
    , picked_position(_alloc)  {
  (void)_alloc;
    }



   typedef std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> _wallselection_type;
  _wallselection_type wallselection;

   typedef std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> _typeselection_type;
  _typeselection_type typeselection;

   typedef std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>> _picked_position_type;
  _picked_position_type picked_position;





  typedef boost::shared_ptr< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> const> ConstPtr;

}; // struct SelectionWall_

typedef ::my_robot_wallinterfaces::SelectionWall_<std::allocator<void> > SelectionWall;

typedef boost::shared_ptr< ::my_robot_wallinterfaces::SelectionWall > SelectionWallPtr;
typedef boost::shared_ptr< ::my_robot_wallinterfaces::SelectionWall const> SelectionWallConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> >::stream(s, "", v);
return s;
}


template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator==(const ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator1> & lhs, const ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator2> & rhs)
{
  return lhs.wallselection == rhs.wallselection &&
    lhs.typeselection == rhs.typeselection &&
    lhs.picked_position == rhs.picked_position;
}

template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator!=(const ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator1> & lhs, const ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator2> & rhs)
{
  return !(lhs == rhs);
}


} // namespace my_robot_wallinterfaces

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsMessage< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> const>
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> const>
  : FalseType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> >
{
  static const char* value()
  {
    return "cec1748b8474fc5db64b113998095031";
  }

  static const char* value(const ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0xcec1748b8474fc5dULL;
  static const uint64_t static_value2 = 0xb64b113998095031ULL;
};

template<class ContainerAllocator>
struct DataType< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> >
{
  static const char* value()
  {
    return "my_robot_wallinterfaces/SelectionWall";
  }

  static const char* value(const ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> >
{
  static const char* value()
  {
    return "string wallselection\n"
"string typeselection\n"
"int32[] picked_position\n"
;
  }

  static const char* value(const ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.wallselection);
      stream.next(m.typeselection);
      stream.next(m.picked_position);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct SelectionWall_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::my_robot_wallinterfaces::SelectionWall_<ContainerAllocator>& v)
  {
    s << indent << "wallselection: ";
    Printer<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>::stream(s, indent + "  ", v.wallselection);
    s << indent << "typeselection: ";
    Printer<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>::stream(s, indent + "  ", v.typeselection);
    s << indent << "picked_position[]" << std::endl;
    for (size_t i = 0; i < v.picked_position.size(); ++i)
    {
      s << indent << "  picked_position[" << i << "]: ";
      Printer<int32_t>::stream(s, indent + "  ", v.picked_position[i]);
    }
  }
};

} // namespace message_operations
} // namespace ros

#endif // MY_ROBOT_WALLINTERFACES_MESSAGE_SELECTIONWALL_H
