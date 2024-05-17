// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from test_package_msg:srv/Tcp.idl
// generated code does not contain a copyright notice

#ifndef TEST_PACKAGE_MSG__SRV__DETAIL__TCP__STRUCT_H_
#define TEST_PACKAGE_MSG__SRV__DETAIL__TCP__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'kiosk_location'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/Tcp in the package test_package_msg.
typedef struct test_package_msg__srv__Tcp_Request
{
  rosidl_runtime_c__String kiosk_location;
} test_package_msg__srv__Tcp_Request;

// Struct for a sequence of test_package_msg__srv__Tcp_Request.
typedef struct test_package_msg__srv__Tcp_Request__Sequence
{
  test_package_msg__srv__Tcp_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} test_package_msg__srv__Tcp_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'response'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/Tcp in the package test_package_msg.
typedef struct test_package_msg__srv__Tcp_Response
{
  rosidl_runtime_c__String response;
} test_package_msg__srv__Tcp_Response;

// Struct for a sequence of test_package_msg__srv__Tcp_Response.
typedef struct test_package_msg__srv__Tcp_Response__Sequence
{
  test_package_msg__srv__Tcp_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} test_package_msg__srv__Tcp_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // TEST_PACKAGE_MSG__SRV__DETAIL__TCP__STRUCT_H_
