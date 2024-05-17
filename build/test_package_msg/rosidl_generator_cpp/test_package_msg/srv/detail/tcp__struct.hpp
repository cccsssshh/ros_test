// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from test_package_msg:srv/Tcp.idl
// generated code does not contain a copyright notice

#ifndef TEST_PACKAGE_MSG__SRV__DETAIL__TCP__STRUCT_HPP_
#define TEST_PACKAGE_MSG__SRV__DETAIL__TCP__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__test_package_msg__srv__Tcp_Request __attribute__((deprecated))
#else
# define DEPRECATED__test_package_msg__srv__Tcp_Request __declspec(deprecated)
#endif

namespace test_package_msg
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Tcp_Request_
{
  using Type = Tcp_Request_<ContainerAllocator>;

  explicit Tcp_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->kiosk_location = "";
    }
  }

  explicit Tcp_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : kiosk_location(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->kiosk_location = "";
    }
  }

  // field types and members
  using _kiosk_location_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _kiosk_location_type kiosk_location;

  // setters for named parameter idiom
  Type & set__kiosk_location(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->kiosk_location = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    test_package_msg::srv::Tcp_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const test_package_msg::srv::Tcp_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<test_package_msg::srv::Tcp_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<test_package_msg::srv::Tcp_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      test_package_msg::srv::Tcp_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<test_package_msg::srv::Tcp_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      test_package_msg::srv::Tcp_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<test_package_msg::srv::Tcp_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<test_package_msg::srv::Tcp_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<test_package_msg::srv::Tcp_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__test_package_msg__srv__Tcp_Request
    std::shared_ptr<test_package_msg::srv::Tcp_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__test_package_msg__srv__Tcp_Request
    std::shared_ptr<test_package_msg::srv::Tcp_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Tcp_Request_ & other) const
  {
    if (this->kiosk_location != other.kiosk_location) {
      return false;
    }
    return true;
  }
  bool operator!=(const Tcp_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Tcp_Request_

// alias to use template instance with default allocator
using Tcp_Request =
  test_package_msg::srv::Tcp_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace test_package_msg


#ifndef _WIN32
# define DEPRECATED__test_package_msg__srv__Tcp_Response __attribute__((deprecated))
#else
# define DEPRECATED__test_package_msg__srv__Tcp_Response __declspec(deprecated)
#endif

namespace test_package_msg
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Tcp_Response_
{
  using Type = Tcp_Response_<ContainerAllocator>;

  explicit Tcp_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  explicit Tcp_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  // field types and members
  using _structure_needs_at_least_one_member_type =
    uint8_t;
  _structure_needs_at_least_one_member_type structure_needs_at_least_one_member;


  // constant declarations

  // pointer types
  using RawPtr =
    test_package_msg::srv::Tcp_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const test_package_msg::srv::Tcp_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<test_package_msg::srv::Tcp_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<test_package_msg::srv::Tcp_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      test_package_msg::srv::Tcp_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<test_package_msg::srv::Tcp_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      test_package_msg::srv::Tcp_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<test_package_msg::srv::Tcp_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<test_package_msg::srv::Tcp_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<test_package_msg::srv::Tcp_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__test_package_msg__srv__Tcp_Response
    std::shared_ptr<test_package_msg::srv::Tcp_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__test_package_msg__srv__Tcp_Response
    std::shared_ptr<test_package_msg::srv::Tcp_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Tcp_Response_ & other) const
  {
    if (this->structure_needs_at_least_one_member != other.structure_needs_at_least_one_member) {
      return false;
    }
    return true;
  }
  bool operator!=(const Tcp_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Tcp_Response_

// alias to use template instance with default allocator
using Tcp_Response =
  test_package_msg::srv::Tcp_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace test_package_msg

namespace test_package_msg
{

namespace srv
{

struct Tcp
{
  using Request = test_package_msg::srv::Tcp_Request;
  using Response = test_package_msg::srv::Tcp_Response;
};

}  // namespace srv

}  // namespace test_package_msg

#endif  // TEST_PACKAGE_MSG__SRV__DETAIL__TCP__STRUCT_HPP_
