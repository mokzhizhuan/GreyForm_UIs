// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from my_robot_wallinterfaces:msg/CombinedMessage.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "my_robot_wallinterfaces/msg/detail/combined_message__struct.h"
#include "my_robot_wallinterfaces/msg/detail/combined_message__functions.h"

bool my_robot_wallinterfaces__msg__selection_wall__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * my_robot_wallinterfaces__msg__selection_wall__convert_to_py(void * raw_ros_message);
bool my_robot_wallinterfaces__msg__file_extraction_message__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * my_robot_wallinterfaces__msg__file_extraction_message__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool my_robot_wallinterfaces__msg__combined_message__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[62];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("my_robot_wallinterfaces.msg._combined_message.CombinedMessage", full_classname_dest, 61) == 0);
  }
  my_robot_wallinterfaces__msg__CombinedMessage * ros_message = _ros_message;
  {  // wall_extraction
    PyObject * field = PyObject_GetAttrString(_pymsg, "wall_extraction");
    if (!field) {
      return false;
    }
    if (!my_robot_wallinterfaces__msg__selection_wall__convert_from_py(field, &ros_message->wall_extraction)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // file_extraction
    PyObject * field = PyObject_GetAttrString(_pymsg, "file_extraction");
    if (!field) {
      return false;
    }
    if (!my_robot_wallinterfaces__msg__file_extraction_message__convert_from_py(field, &ros_message->file_extraction)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * my_robot_wallinterfaces__msg__combined_message__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of CombinedMessage */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("my_robot_wallinterfaces.msg._combined_message");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "CombinedMessage");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  my_robot_wallinterfaces__msg__CombinedMessage * ros_message = (my_robot_wallinterfaces__msg__CombinedMessage *)raw_ros_message;
  {  // wall_extraction
    PyObject * field = NULL;
    field = my_robot_wallinterfaces__msg__selection_wall__convert_to_py(&ros_message->wall_extraction);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "wall_extraction", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // file_extraction
    PyObject * field = NULL;
    field = my_robot_wallinterfaces__msg__file_extraction_message__convert_to_py(&ros_message->file_extraction);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "file_extraction", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
