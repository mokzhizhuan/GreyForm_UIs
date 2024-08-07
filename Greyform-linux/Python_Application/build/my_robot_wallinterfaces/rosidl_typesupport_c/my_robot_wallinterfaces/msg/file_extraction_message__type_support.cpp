// generated from rosidl_typesupport_c/resource/idl__type_support.cpp.em
// with input from my_robot_wallinterfaces:msg/FileExtractionMessage.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__struct.h"
#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__type_support.h"
#include "rosidl_typesupport_c/identifier.h"
#include "rosidl_typesupport_c/message_type_support_dispatch.h"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_c/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace my_robot_wallinterfaces
{

namespace msg
{

namespace rosidl_typesupport_c
{

typedef struct _FileExtractionMessage_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _FileExtractionMessage_type_support_ids_t;

static const _FileExtractionMessage_type_support_ids_t _FileExtractionMessage_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_c",  // ::rosidl_typesupport_fastrtps_c::typesupport_identifier,
    "rosidl_typesupport_introspection_c",  // ::rosidl_typesupport_introspection_c::typesupport_identifier,
  }
};

typedef struct _FileExtractionMessage_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _FileExtractionMessage_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _FileExtractionMessage_type_support_symbol_names_t _FileExtractionMessage_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, my_robot_wallinterfaces, msg, FileExtractionMessage)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, my_robot_wallinterfaces, msg, FileExtractionMessage)),
  }
};

typedef struct _FileExtractionMessage_type_support_data_t
{
  void * data[2];
} _FileExtractionMessage_type_support_data_t;

static _FileExtractionMessage_type_support_data_t _FileExtractionMessage_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _FileExtractionMessage_message_typesupport_map = {
  2,
  "my_robot_wallinterfaces",
  &_FileExtractionMessage_message_typesupport_ids.typesupport_identifier[0],
  &_FileExtractionMessage_message_typesupport_symbol_names.symbol_name[0],
  &_FileExtractionMessage_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t FileExtractionMessage_message_type_support_handle = {
  rosidl_typesupport_c__typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_FileExtractionMessage_message_typesupport_map),
  rosidl_typesupport_c__get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_c

}  // namespace msg

}  // namespace my_robot_wallinterfaces

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_c, my_robot_wallinterfaces, msg, FileExtractionMessage)() {
  return &::my_robot_wallinterfaces::msg::rosidl_typesupport_c::FileExtractionMessage_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
