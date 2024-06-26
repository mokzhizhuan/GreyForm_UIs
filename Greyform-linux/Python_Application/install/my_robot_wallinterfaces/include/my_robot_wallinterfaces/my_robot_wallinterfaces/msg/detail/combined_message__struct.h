// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from my_robot_wallinterfaces:msg/CombinedMessage.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__STRUCT_H_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'wall_extraction'
#include "my_robot_wallinterfaces/msg/detail/selection_wall__struct.h"
// Member 'file_extraction'
#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__struct.h"

/// Struct defined in msg/CombinedMessage in the package my_robot_wallinterfaces.
typedef struct my_robot_wallinterfaces__msg__CombinedMessage
{
  my_robot_wallinterfaces__msg__SelectionWall wall_extraction;
  my_robot_wallinterfaces__msg__FileExtractionMessage file_extraction;
} my_robot_wallinterfaces__msg__CombinedMessage;

// Struct for a sequence of my_robot_wallinterfaces__msg__CombinedMessage.
typedef struct my_robot_wallinterfaces__msg__CombinedMessage__Sequence
{
  my_robot_wallinterfaces__msg__CombinedMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} my_robot_wallinterfaces__msg__CombinedMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__COMBINED_MESSAGE__STRUCT_H_
