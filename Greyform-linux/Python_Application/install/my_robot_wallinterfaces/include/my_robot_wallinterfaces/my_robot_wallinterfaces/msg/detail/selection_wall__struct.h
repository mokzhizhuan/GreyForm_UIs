// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from my_robot_wallinterfaces:msg/SelectionWall.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__STRUCT_H_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'wallselection'
// Member 'typeselection'
#include "rosidl_runtime_c/string.h"
// Member 'picked_position'
// Member 'default_position'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/SelectionWall in the package my_robot_wallinterfaces.
typedef struct my_robot_wallinterfaces__msg__SelectionWall
{
  rosidl_runtime_c__String wallselection;
  rosidl_runtime_c__String typeselection;
  int32_t sectionselection;
  rosidl_runtime_c__int32__Sequence picked_position;
  rosidl_runtime_c__int32__Sequence default_position;
} my_robot_wallinterfaces__msg__SelectionWall;

// Struct for a sequence of my_robot_wallinterfaces__msg__SelectionWall.
typedef struct my_robot_wallinterfaces__msg__SelectionWall__Sequence
{
  my_robot_wallinterfaces__msg__SelectionWall * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} my_robot_wallinterfaces__msg__SelectionWall__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__SELECTION_WALL__STRUCT_H_
