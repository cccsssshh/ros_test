// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from test_package_msg:srv/Tcp.idl
// generated code does not contain a copyright notice

#ifndef TEST_PACKAGE_MSG__SRV__DETAIL__TCP__BUILDER_HPP_
#define TEST_PACKAGE_MSG__SRV__DETAIL__TCP__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "test_package_msg/srv/detail/tcp__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace test_package_msg
{

namespace srv
{

namespace builder
{

class Init_Tcp_Request_kiosk_location
{
public:
  Init_Tcp_Request_kiosk_location()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::test_package_msg::srv::Tcp_Request kiosk_location(::test_package_msg::srv::Tcp_Request::_kiosk_location_type arg)
  {
    msg_.kiosk_location = std::move(arg);
    return std::move(msg_);
  }

private:
  ::test_package_msg::srv::Tcp_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::test_package_msg::srv::Tcp_Request>()
{
  return test_package_msg::srv::builder::Init_Tcp_Request_kiosk_location();
}

}  // namespace test_package_msg


namespace test_package_msg
{

namespace srv
{


}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::test_package_msg::srv::Tcp_Response>()
{
  return ::test_package_msg::srv::Tcp_Response(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace test_package_msg

#endif  // TEST_PACKAGE_MSG__SRV__DETAIL__TCP__BUILDER_HPP_
