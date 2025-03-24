// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from my_robot_wallinterfaces:msg/FileExtractionMessage.idl
// generated code does not contain a copyright notice

#ifndef MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__STRUCT_H_
#define MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'stl_data'
#include "rosidl_runtime_c/primitives_sequence.h"
// Member 'excelfile'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/FileExtractionMessage in the package my_robot_wallinterfaces.
typedef struct my_robot_wallinterfaces__msg__FileExtractionMessage
{
  rosidl_runtime_c__uint8__Sequence stl_data;
  rosidl_runtime_c__String excelfile;
} my_robot_wallinterfaces__msg__FileExtractionMessage;

// Struct for a sequence of my_robot_wallinterfaces__msg__FileExtractionMessage.
typedef struct my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence
{
  my_robot_wallinterfaces__msg__FileExtractionMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MY_ROBOT_WALLINTERFACES__MSG__DETAIL__FILE_EXTRACTION_MESSAGE__STRUCT_H_
