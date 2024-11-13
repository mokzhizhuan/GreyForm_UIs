// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from my_robot_wallinterfaces:msg/SelectionWall.idl
// generated code does not contain a copyright notice
#include "my_robot_wallinterfaces/msg/detail/selection_wall__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `wallselection`
// Member `typeselection`
#include "rosidl_runtime_c/string_functions.h"
// Member `picked_position`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
my_robot_wallinterfaces__msg__SelectionWall__init(my_robot_wallinterfaces__msg__SelectionWall * msg)
{
  if (!msg) {
    return false;
  }
  // wallselection
  if (!rosidl_runtime_c__String__init(&msg->wallselection)) {
    my_robot_wallinterfaces__msg__SelectionWall__fini(msg);
    return false;
  }
  // typeselection
  if (!rosidl_runtime_c__String__init(&msg->typeselection)) {
    my_robot_wallinterfaces__msg__SelectionWall__fini(msg);
    return false;
  }
  // sectionselection
  // picked_position
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->picked_position, 0)) {
    my_robot_wallinterfaces__msg__SelectionWall__fini(msg);
    return false;
  }
  return true;
}

void
my_robot_wallinterfaces__msg__SelectionWall__fini(my_robot_wallinterfaces__msg__SelectionWall * msg)
{
  if (!msg) {
    return;
  }
  // wallselection
  rosidl_runtime_c__String__fini(&msg->wallselection);
  // typeselection
  rosidl_runtime_c__String__fini(&msg->typeselection);
  // sectionselection
  // picked_position
  rosidl_runtime_c__int32__Sequence__fini(&msg->picked_position);
}

bool
my_robot_wallinterfaces__msg__SelectionWall__are_equal(const my_robot_wallinterfaces__msg__SelectionWall * lhs, const my_robot_wallinterfaces__msg__SelectionWall * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // wallselection
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->wallselection), &(rhs->wallselection)))
  {
    return false;
  }
  // typeselection
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->typeselection), &(rhs->typeselection)))
  {
    return false;
  }
  // sectionselection
  if (lhs->sectionselection != rhs->sectionselection) {
    return false;
  }
  // picked_position
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->picked_position), &(rhs->picked_position)))
  {
    return false;
  }
  return true;
}

bool
my_robot_wallinterfaces__msg__SelectionWall__copy(
  const my_robot_wallinterfaces__msg__SelectionWall * input,
  my_robot_wallinterfaces__msg__SelectionWall * output)
{
  if (!input || !output) {
    return false;
  }
  // wallselection
  if (!rosidl_runtime_c__String__copy(
      &(input->wallselection), &(output->wallselection)))
  {
    return false;
  }
  // typeselection
  if (!rosidl_runtime_c__String__copy(
      &(input->typeselection), &(output->typeselection)))
  {
    return false;
  }
  // sectionselection
  output->sectionselection = input->sectionselection;
  // picked_position
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->picked_position), &(output->picked_position)))
  {
    return false;
  }
  return true;
}

my_robot_wallinterfaces__msg__SelectionWall *
my_robot_wallinterfaces__msg__SelectionWall__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  my_robot_wallinterfaces__msg__SelectionWall * msg = (my_robot_wallinterfaces__msg__SelectionWall *)allocator.allocate(sizeof(my_robot_wallinterfaces__msg__SelectionWall), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(my_robot_wallinterfaces__msg__SelectionWall));
  bool success = my_robot_wallinterfaces__msg__SelectionWall__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
my_robot_wallinterfaces__msg__SelectionWall__destroy(my_robot_wallinterfaces__msg__SelectionWall * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    my_robot_wallinterfaces__msg__SelectionWall__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
my_robot_wallinterfaces__msg__SelectionWall__Sequence__init(my_robot_wallinterfaces__msg__SelectionWall__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  my_robot_wallinterfaces__msg__SelectionWall * data = NULL;

  if (size) {
    data = (my_robot_wallinterfaces__msg__SelectionWall *)allocator.zero_allocate(size, sizeof(my_robot_wallinterfaces__msg__SelectionWall), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = my_robot_wallinterfaces__msg__SelectionWall__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        my_robot_wallinterfaces__msg__SelectionWall__fini(&data[i - 1]);
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
my_robot_wallinterfaces__msg__SelectionWall__Sequence__fini(my_robot_wallinterfaces__msg__SelectionWall__Sequence * array)
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
      my_robot_wallinterfaces__msg__SelectionWall__fini(&array->data[i]);
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

my_robot_wallinterfaces__msg__SelectionWall__Sequence *
my_robot_wallinterfaces__msg__SelectionWall__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  my_robot_wallinterfaces__msg__SelectionWall__Sequence * array = (my_robot_wallinterfaces__msg__SelectionWall__Sequence *)allocator.allocate(sizeof(my_robot_wallinterfaces__msg__SelectionWall__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = my_robot_wallinterfaces__msg__SelectionWall__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
my_robot_wallinterfaces__msg__SelectionWall__Sequence__destroy(my_robot_wallinterfaces__msg__SelectionWall__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    my_robot_wallinterfaces__msg__SelectionWall__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
my_robot_wallinterfaces__msg__SelectionWall__Sequence__are_equal(const my_robot_wallinterfaces__msg__SelectionWall__Sequence * lhs, const my_robot_wallinterfaces__msg__SelectionWall__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!my_robot_wallinterfaces__msg__SelectionWall__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
my_robot_wallinterfaces__msg__SelectionWall__Sequence__copy(
  const my_robot_wallinterfaces__msg__SelectionWall__Sequence * input,
  my_robot_wallinterfaces__msg__SelectionWall__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(my_robot_wallinterfaces__msg__SelectionWall);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    my_robot_wallinterfaces__msg__SelectionWall * data =
      (my_robot_wallinterfaces__msg__SelectionWall *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!my_robot_wallinterfaces__msg__SelectionWall__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          my_robot_wallinterfaces__msg__SelectionWall__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!my_robot_wallinterfaces__msg__SelectionWall__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
