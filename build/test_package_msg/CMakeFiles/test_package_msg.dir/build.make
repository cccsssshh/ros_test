# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.22

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/addinedu/test/test_project/src/test_package_msg

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/addinedu/test/test_project/build/test_package_msg

# Utility rule file for test_package_msg.

# Include any custom commands dependencies for this target.
include CMakeFiles/test_package_msg.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/test_package_msg.dir/progress.make

CMakeFiles/test_package_msg: /home/addinedu/test/test_project/src/test_package_msg/srv/Tcp.srv
CMakeFiles/test_package_msg: rosidl_cmake/srv/Tcp_Request.msg
CMakeFiles/test_package_msg: rosidl_cmake/srv/Tcp_Response.msg

test_package_msg: CMakeFiles/test_package_msg
test_package_msg: CMakeFiles/test_package_msg.dir/build.make
.PHONY : test_package_msg

# Rule to build all files generated by this target.
CMakeFiles/test_package_msg.dir/build: test_package_msg
.PHONY : CMakeFiles/test_package_msg.dir/build

CMakeFiles/test_package_msg.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/test_package_msg.dir/cmake_clean.cmake
.PHONY : CMakeFiles/test_package_msg.dir/clean

CMakeFiles/test_package_msg.dir/depend:
	cd /home/addinedu/test/test_project/build/test_package_msg && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/addinedu/test/test_project/src/test_package_msg /home/addinedu/test/test_project/src/test_package_msg /home/addinedu/test/test_project/build/test_package_msg /home/addinedu/test/test_project/build/test_package_msg /home/addinedu/test/test_project/build/test_package_msg/CMakeFiles/test_package_msg.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/test_package_msg.dir/depend

