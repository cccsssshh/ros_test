// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from test_package_msg:srv/Tcp.idl
// generated code does not contain a copyright notice

#ifndef TEST_PACKAGE_MSG__SRV__DETAIL__TCP__TRAITS_HPP_
#define TEST_PACKAGE_MSG__SRV__DETAIL__TCP__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "test_package_msg/srv/detail/tcp__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace test_package_msg
{

namespace srv
{

inline void to_flow_style_yaml(
  const Tcp_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: kiosk_location
  {
    out << "kiosk_location: ";
    rosidl_generator_traits::value_to_yaml(msg.kiosk_location, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Tcp_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: kiosk_location
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "kiosk_location: ";
    rosidl_generator_traits::value_to_yaml(msg.kiosk_location, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Tcp_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace test_package_msg

namespace rosidl_generator_traits
{

[[deprecated("use test_package_msg::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const test_package_msg::srv::Tcp_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  test_package_msg::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use test_package_msg::srv::to_yaml() instead")]]
inline std::string to_yaml(const test_package_msg::srv::Tcp_Request & msg)
{
  return test_package_msg::srv::to_yaml(msg);
}

template<>
inline const char * data_type<test_package_msg::srv::Tcp_Request>()
{
  return "test_package_msg::srv::Tcp_Request";
}

template<>
inline const char * name<test_package_msg::srv::Tcp_Request>()
{
  return "test_package_msg/srv/Tcp_Request";
}

template<>
struct has_fixed_size<test_package_msg::srv::Tcp_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<test_package_msg::srv::Tcp_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<test_package_msg::srv::Tcp_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace test_package_msg
{

namespace srv
{

inline void to_flow_style_yaml(
  const Tcp_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: response
  {
    out << "response: ";
    rosidl_generator_traits::value_to_yaml(msg.response, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Tcp_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: response
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "response: ";
    rosidl_generator_traits::value_to_yaml(msg.response, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Tcp_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace test_package_msg

namespace rosidl_generator_traits
{

[[deprecated("use test_package_msg::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const test_package_msg::srv::Tcp_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  test_package_msg::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use test_package_msg::srv::to_yaml() instead")]]
inline std::string to_yaml(const test_package_msg::srv::Tcp_Response & msg)
{
  return test_package_msg::srv::to_yaml(msg);
}

template<>
inline const char * data_type<test_package_msg::srv::Tcp_Response>()
{
  return "test_package_msg::srv::Tcp_Response";
}

template<>
inline const char * name<test_package_msg::srv::Tcp_Response>()
{
  return "test_package_msg/srv/Tcp_Response";
}

template<>
struct has_fixed_size<test_package_msg::srv::Tcp_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<test_package_msg::srv::Tcp_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<test_package_msg::srv::Tcp_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<test_package_msg::srv::Tcp>()
{
  return "test_package_msg::srv::Tcp";
}

template<>
inline const char * name<test_package_msg::srv::Tcp>()
{
  return "test_package_msg/srv/Tcp";
}

template<>
struct has_fixed_size<test_package_msg::srv::Tcp>
  : std::integral_constant<
    bool,
    has_fixed_size<test_package_msg::srv::Tcp_Request>::value &&
    has_fixed_size<test_package_msg::srv::Tcp_Response>::value
  >
{
};

template<>
struct has_bounded_size<test_package_msg::srv::Tcp>
  : std::integral_constant<
    bool,
    has_bounded_size<test_package_msg::srv::Tcp_Request>::value &&
    has_bounded_size<test_package_msg::srv::Tcp_Response>::value
  >
{
};

template<>
struct is_service<test_package_msg::srv::Tcp>
  : std::true_type
{
};

template<>
struct is_service_request<test_package_msg::srv::Tcp_Request>
  : std::true_type
{
};

template<>
struct is_service_response<test_package_msg::srv::Tcp_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // TEST_PACKAGE_MSG__SRV__DETAIL__TCP__TRAITS_HPP_
