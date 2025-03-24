// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from my_robot_wallinterfaces:msg/FileExtractionMessage.idl
// generated code does not contain a copyright notice
#include "my_robot_wallinterfaces/msg/detail/file_extraction_message__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `stl_data`
#include "rosidl_runtime_c/primitives_sequence_functions.h"
// Member `excelfile`
#include "rosidl_runtime_c/string_functions.h"

bool
my_robot_wallinterfaces__msg__FileExtractionMessage__init(my_robot_wallinterfaces__msg__FileExtractionMessage * msg)
{
  if (!msg) {
    return false;
  }
  // stl_data
  if (!rosidl_runtime_c__uint8__Sequence__init(&msg->stl_data, 0)) {
    my_robot_wallinterfaces__msg__FileExtractionMessage__fini(msg);
    return false;
  }
  // excelfile
  if (!rosidl_runtime_c__String__init(&msg->excelfile)) {
    my_robot_wallinterfaces__msg__FileExtractionMessage__fini(msg);
    return false;
  }
  return true;
}

void
my_robot_wallinterfaces__msg__FileExtractionMessage__fini(my_robot_wallinterfaces__msg__FileExtractionMessage * msg)
{
  if (!msg) {
    return;
  }
  // stl_data
  rosidl_runtime_c__uint8__Sequence__fini(&msg->stl_data);
  // excelfile
  rosidl_runtime_c__String__fini(&msg->excelfile);
}

bool
my_robot_wallinterfaces__msg__FileExtractionMessage__are_equal(const my_robot_wallinterfaces__msg__FileExtractionMessage * lhs, const my_robot_wallinterfaces__msg__FileExtractionMessage * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // stl_data
  if (!rosidl_runtime_c__uint8__Sequence__are_equal(
      &(lhs->stl_data), &(rhs->stl_data)))
  {
    return false;
  }
  // excelfile
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->excelfile), &(rhs->excelfile)))
  {
    return false;
  }
  return true;
}

bool
my_robot_wallinterfaces__msg__FileExtractionMessage__copy(
  const my_robot_wallinterfaces__msg__FileExtractionMessage * input,
  my_robot_wallinterfaces__msg__FileExtractionMessage * output)
{
  if (!input || !output) {
    return false;
  }
  // stl_data
  if (!rosidl_runtime_c__uint8__Sequence__copy(
      &(input->stl_data), &(output->stl_data)))
  {
    return false;
  }
  // excelfile
  if (!rosidl_runtime_c__String__copy(
      &(input->excelfile), &(output->excelfile)))
  {
    return false;
  }
  return true;
}

my_robot_wallinterfaces__msg__FileExtractionMessage *
my_robot_wallinterfaces__msg__FileExtractionMessage__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  my_robot_wallinterfaces__msg__FileExtractionMessage * msg = (my_robot_wallinterfaces__msg__FileExtractionMessage *)allocator.allocate(sizeof(my_robot_wallinterfaces__msg__FileExtractionMessage), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(my_robot_wallinterfaces__msg__FileExtractionMessage));
  bool success = my_robot_wallinterfaces__msg__FileExtractionMessage__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
my_robot_wallinterfaces__msg__FileExtractionMessage__destroy(my_robot_wallinterfaces__msg__FileExtractionMessage * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    my_robot_wallinterfaces__msg__FileExtractionMessage__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence__init(my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  my_robot_wallinterfaces__msg__FileExtractionMessage * data = NULL;

  if (size) {
    data = (my_robot_wallinterfaces__msg__FileExtractionMessage *)allocator.zero_allocate(size, sizeof(my_robot_wallinterfaces__msg__FileExtractionMessage), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = my_robot_wallinterfaces__msg__FileExtractionMessage__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        my_robot_wallinterfaces__msg__FileExtractionMessage__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence__fini(my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      my_robot_wallinterfaces__msg__FileExtractionMessage__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence *
my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence * array = (my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence *)allocator.allocate(sizeof(my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence__destroy(my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence__are_equal(const my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence * lhs, const my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!my_robot_wallinterfaces__msg__FileExtractionMessage__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence__copy(
  const my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence * input,
  my_robot_wallinterfaces__msg__FileExtractionMessage__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(my_robot_wallinterfaces__msg__FileExtractionMessage);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    my_robot_wallinterfaces__msg__FileExtractionMessage * data =
      (my_robot_wallinterfaces__msg__FileExtractionMessage *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!my_robot_wallinterfaces__msg__FileExtractionMessage__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          my_robot_wallinterfaces__msg__FileExtractionMessage__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!my_robot_wallinterfaces__msg__FileExtractionMessage__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
