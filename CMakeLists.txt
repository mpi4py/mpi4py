# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
cmake_minimum_required(VERSION 3.15...3.26)

project(mpi4py LANGUAGES C)

find_package(
  Python REQUIRED
  COMPONENTS Interpreter
  COMPONENTS Development.Module
  OPTIONAL_COMPONENTS Development.Embed
)

find_package(MPI REQUIRED)
separate_arguments(MPI_C_COMPILE_OPTIONS NATIVE_COMMAND)
separate_arguments(MPI_C_LINK_FLAGS NATIVE_COMMAND)


set(BINDIR ${CMAKE_CURRENT_BINARY_DIR})
set(TOPDIR ${CMAKE_CURRENT_SOURCE_DIR})
set(SRCDIR ${CMAKE_CURRENT_SOURCE_DIR}/src)


# intelmpi.pth
include(CheckSymbolExists)
set(CMAKE_REQUIRED_INCLUDES ${MPI_C_INCLUDE_PATH})
check_symbol_exists(I_MPI_VERSION "mpi.h" HAVE_I_MPI_VERSION)
if (HAVE_I_MPI_VERSION AND WIN32)
  set(intelmpi.pth ${BINDIR}/intelmpi.pth)
  configure_file(${SRCDIR}/intelmpi.pth ${intelmpi.pth} COPYONLY)
  install(FILES ${intelmpi.pth} DESTINATION .)
endif()


# mpi4py/mpi.cfg
set(mpi.cfg ${BINDIR}/mpi.cfg)
set(config "[mpi]\n")
if (MPI_C_COMPILER)
  set(config "${config}mpicc = ${MPI_C_COMPILER}\n")
endif()
if (MPI_CXX_COMPILER)
  set(config "${config}mpicxx = ${MPI_CXX_COMPILER}\n")
endif()
if (MPI_Fortran_COMPILER)
  set(config "${config}mpifort = ${MPI_Fortran_COMPILER}\n")
endif()
file(GENERATE OUTPUT ${mpi.cfg} CONTENT ${config})
install(FILES ${mpi.cfg} DESTINATION mpi4py)


# Cython
set(cythonize ${TOPDIR}/conf/cythonize.py)
set(Cython_COMMAND ${Python_EXECUTABLE} ${cythonize})
set(Cython_OPTIONS -3 --cleanup 3)
set(MPI.pyx ${SRCDIR}/mpi4py/MPI.pyx)
file(
  GLOB_RECURSE MPI.deps
  ${SRCDIR}/mpi4py/*.pyx
  ${SRCDIR}/mpi4py/*.pxd
  ${SRCDIR}/mpi4py/MPI/*.pyx
  ${SRCDIR}/mpi4py/MPI/*.pxi
)
set(MPI.c ${BINDIR}/MPI.c)
set(MPI.h ${BINDIR}/MPI.h ${BINDIR}/MPI_api.h)
add_custom_command(
  OUTPUT ${MPI.c}
  BYPRODUCTS ${MPI.h}
  DEPENDS ${MPI.deps}
  VERBATIM
  COMMAND
  ${Cython_COMMAND} ${Cython_OPTIONS}
  --working ${SRCDIR} ${MPI.pyx}
  --output-file ${MPI.c}
)
install(FILES ${MPI.h} DESTINATION mpi4py)


# mpi4py.MPI
python_add_library(mpi4py.MPI MODULE ${MPI.c} WITH_SOABI)
set_target_properties(mpi4py.MPI PROPERTIES OUTPUT_NAME "MPI" PREFIX "")
target_include_directories(mpi4py.MPI PRIVATE ${SRCDIR})
target_include_directories(mpi4py.MPI PRIVATE ${MPI_C_INCLUDE_DIRS})
target_compile_definitions(mpi4py.MPI PRIVATE ${MPI_C_COMPILE_DEFINITIONS})
target_compile_options(mpi4py.MPI PRIVATE ${MPI_C_COMPILE_OPTIONS})
target_link_directories(mpi4py.MPI PRIVATE ${MPI_C_LIBRARY_DIRS})
target_link_libraries(mpi4py.MPI PRIVATE ${MPI_C_LIBRARIES})
target_link_options(mpi4py.MPI PRIVATE ${MPI_C_LINK_FLAGS})
install(TARGETS mpi4py.MPI LIBRARY DESTINATION mpi4py)

# mpi4py/bin/python-mpi
if (Python_Development.Embed_FOUND)
add_executable(python-mpi ${SRCDIR}/python.c)
target_include_directories(python-mpi PRIVATE ${Python_INCLUDE_DIRS})
target_link_directories(python-mpi PRIVATE ${Python_LIBRARY_DIRS})
target_link_libraries(python-mpi PRIVATE ${Python_LIBRARIES})
target_include_directories(python-mpi PRIVATE ${MPI_C_INCLUDE_DIRS})
target_compile_definitions(python-mpi PRIVATE ${MPI_C_COMPILE_DEFINITIONS})
target_compile_options(python-mpi PRIVATE ${MPI_C_COMPILE_OPTIONS})
target_link_directories(python-mpi PRIVATE ${MPI_C_LIBRARY_DIRS})
target_link_libraries(python-mpi PRIVATE ${MPI_C_LIBRARIES})
target_link_options(python-mpi PRIVATE ${MPI_C_LINK_FLAGS})
install(TARGETS python-mpi RUNTIME DESTINATION mpi4py/bin)
endif()


# mpi4py/*
file(
  GLOB mpi4py_SOURCES
  RELATIVE ${SRCDIR}
  ${SRCDIR}/mpi4py/*.py
  ${SRCDIR}/mpi4py/*.pyi
  ${SRCDIR}/mpi4py/*.pxd
  ${SRCDIR}/mpi4py/py.typed
  ${SRCDIR}/mpi4py/futures/*.py
  ${SRCDIR}/mpi4py/futures/*.pyi
  ${SRCDIR}/mpi4py/util/*.py
  ${SRCDIR}/mpi4py/util/*.pyi
)
file(
  GLOB mpi4py_HEADERS
  RELATIVE ${SRCDIR}
  ${SRCDIR}/mpi4py/include/mpi4py/*.[hi]
  ${SRCDIR}/mpi4py/include/mpi4py/*.px[di]
)
foreach(file ${mpi4py_SOURCES} ${mpi4py_HEADERS})
  get_filename_component(dir ${file} DIRECTORY)
  install(FILES ${SRCDIR}/${file} DESTINATION ${dir})
endforeach()
