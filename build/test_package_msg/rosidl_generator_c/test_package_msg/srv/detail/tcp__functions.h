// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from test_package_msg:srv/Tcp.idl
// generated code does not contain a copyright notice

#ifndef TEST_PACKAGE_MSG__SRV__DETAIL__TCP__FUNCTIONS_H_
#define TEST_PACKAGE_MSG__SRV__DETAIL__TCP__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "test_package_msg/msg/rosidl_generator_c__visibility_control.h"

#include "test_package_msg/srv/detail/tcp__struct.h"

/// Initialize srv/Tcp message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * test_package_msg__srv__Tcp_Request
 * )) before or use
 * test_package_msg__srv__Tcp_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Request__init(test_package_msg__srv__Tcp_Request * msg);

/// Finalize srv/Tcp message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
void
test_package_msg__srv__Tcp_Request__fini(test_package_msg__srv__Tcp_Request * msg);

/// Create srv/Tcp message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * test_package_msg__srv__Tcp_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
test_package_msg__srv__Tcp_Request *
test_package_msg__srv__Tcp_Request__create();

/// Destroy srv/Tcp message.
/**
 * It calls
 * test_package_msg__srv__Tcp_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
void
test_package_msg__srv__Tcp_Request__destroy(test_package_msg__srv__Tcp_Request * msg);

/// Check for srv/Tcp message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Request__are_equal(const test_package_msg__srv__Tcp_Request * lhs, const test_package_msg__srv__Tcp_Request * rhs);

/// Copy a srv/Tcp message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Request__copy(
  const test_package_msg__srv__Tcp_Request * input,
  test_package_msg__srv__Tcp_Request * output);

/// Initialize array of srv/Tcp messages.
/**
 * It allocates the memory for the number of elements and calls
 * test_package_msg__srv__Tcp_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Request__Sequence__init(test_package_msg__srv__Tcp_Request__Sequence * array, size_t size);

/// Finalize array of srv/Tcp messages.
/**
 * It calls
 * test_package_msg__srv__Tcp_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
void
test_package_msg__srv__Tcp_Request__Sequence__fini(test_package_msg__srv__Tcp_Request__Sequence * array);

/// Create array of srv/Tcp messages.
/**
 * It allocates the memory for the array and calls
 * test_package_msg__srv__Tcp_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
test_package_msg__srv__Tcp_Request__Sequence *
test_package_msg__srv__Tcp_Request__Sequence__create(size_t size);

/// Destroy array of srv/Tcp messages.
/**
 * It calls
 * test_package_msg__srv__Tcp_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
void
test_package_msg__srv__Tcp_Request__Sequence__destroy(test_package_msg__srv__Tcp_Request__Sequence * array);

/// Check for srv/Tcp message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Request__Sequence__are_equal(const test_package_msg__srv__Tcp_Request__Sequence * lhs, const test_package_msg__srv__Tcp_Request__Sequence * rhs);

/// Copy an array of srv/Tcp messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Request__Sequence__copy(
  const test_package_msg__srv__Tcp_Request__Sequence * input,
  test_package_msg__srv__Tcp_Request__Sequence * output);

/// Initialize srv/Tcp message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * test_package_msg__srv__Tcp_Response
 * )) before or use
 * test_package_msg__srv__Tcp_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Response__init(test_package_msg__srv__Tcp_Response * msg);

/// Finalize srv/Tcp message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
void
test_package_msg__srv__Tcp_Response__fini(test_package_msg__srv__Tcp_Response * msg);

/// Create srv/Tcp message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * test_package_msg__srv__Tcp_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
test_package_msg__srv__Tcp_Response *
test_package_msg__srv__Tcp_Response__create();

/// Destroy srv/Tcp message.
/**
 * It calls
 * test_package_msg__srv__Tcp_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
void
test_package_msg__srv__Tcp_Response__destroy(test_package_msg__srv__Tcp_Response * msg);

/// Check for srv/Tcp message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Response__are_equal(const test_package_msg__srv__Tcp_Response * lhs, const test_package_msg__srv__Tcp_Response * rhs);

/// Copy a srv/Tcp message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Response__copy(
  const test_package_msg__srv__Tcp_Response * input,
  test_package_msg__srv__Tcp_Response * output);

/// Initialize array of srv/Tcp messages.
/**
 * It allocates the memory for the number of elements and calls
 * test_package_msg__srv__Tcp_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Response__Sequence__init(test_package_msg__srv__Tcp_Response__Sequence * array, size_t size);

/// Finalize array of srv/Tcp messages.
/**
 * It calls
 * test_package_msg__srv__Tcp_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
void
test_package_msg__srv__Tcp_Response__Sequence__fini(test_package_msg__srv__Tcp_Response__Sequence * array);

/// Create array of srv/Tcp messages.
/**
 * It allocates the memory for the array and calls
 * test_package_msg__srv__Tcp_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
test_package_msg__srv__Tcp_Response__Sequence *
test_package_msg__srv__Tcp_Response__Sequence__create(size_t size);

/// Destroy array of srv/Tcp messages.
/**
 * It calls
 * test_package_msg__srv__Tcp_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
void
test_package_msg__srv__Tcp_Response__Sequence__destroy(test_package_msg__srv__Tcp_Response__Sequence * array);

/// Check for srv/Tcp message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Response__Sequence__are_equal(const test_package_msg__srv__Tcp_Response__Sequence * lhs, const test_package_msg__srv__Tcp_Response__Sequence * rhs);

/// Copy an array of srv/Tcp messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_test_package_msg
bool
test_package_msg__srv__Tcp_Response__Sequence__copy(
  const test_package_msg__srv__Tcp_Response__Sequence * input,
  test_package_msg__srv__Tcp_Response__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // TEST_PACKAGE_MSG__SRV__DETAIL__TCP__FUNCTIONS_H_
