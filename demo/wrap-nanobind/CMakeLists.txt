cmake_minimum_required(VERSION 3.15...3.27)
project(helloworld)

if (CMAKE_VERSION VERSION_LESS 3.18)
  set(DEV_MODULE Development)
else()
  set(DEV_MODULE Development.Module)
endif()

set(Python_FIND_UNVERSIONED_NAMES FIRST)
find_package(Python 3.10 COMPONENTS Interpreter ${DEV_MODULE} REQUIRED)

find_package(MPI REQUIRED)

execute_process(
  COMMAND "${Python_EXECUTABLE}" -m mpi4py --prefix
  OUTPUT_STRIP_TRAILING_WHITESPACE
  OUTPUT_VARIABLE mpi4py_ROOT
)
set(mpi4py_INCLUDE ${mpi4py_ROOT}/include)

execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE
  OUTPUT_VARIABLE nanobind_ROOT
)
find_package(nanobind CONFIG REQUIRED)

if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

nanobind_add_module(helloworld helloworld.cxx)
target_include_directories(helloworld PRIVATE ${mpi4py_INCLUDE})
target_include_directories(helloworld PRIVATE MPI::MPI_C)
target_link_libraries(helloworld PRIVATE MPI::MPI_C)
install(TARGETS helloworld LIBRARY DESTINATION .)
