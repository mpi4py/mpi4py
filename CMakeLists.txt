# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
cmake_minimum_required(VERSION 3.15...3.26)
project(mpi4py LANGUAGES C)

set(
  MPIABI $ENV{MPI4PY_BUILD_MPIABI} CACHE BOOL
  "Use MPI ABI (standard or legacy)"
)
set(
  PYSABI $ENV{MPI4PY_BUILD_PYSABI} CACHE STRING
  "Use Python Stable ABI"
)

if (PYSABI)
  if (NOT SKBUILD_SABI_COMPONENT)
    set(SKBUILD_SABI_COMPONENT Development.SABIModule)
  endif()
  if (NOT SKBUILD_SABI_VERSION)
    set(SKBUILD_SABI_VERSION ${PYSABI})
  endif()
endif()
if (SKBUILD_SABI_VERSION)
  set(WITH_SABI USE_SABI ${SKBUILD_SABI_VERSION})
endif()

find_package(
  Python REQUIRED
  COMPONENTS Interpreter
  COMPONENTS Development.Module ${SKBUILD_SABI_COMPONENT}
  OPTIONAL_COMPONENTS Development.Embed
)

find_package(MPI)

set(BINDIR ${CMAKE_CURRENT_BINARY_DIR})
set(TOPDIR ${CMAKE_CURRENT_SOURCE_DIR})
set(SRCDIR ${CMAKE_CURRENT_SOURCE_DIR}/src)


# MPI ABI stub library
if (NOT MPI_FOUND)
  set(ABIDIR ${SRCDIR}/abi-stub)
  add_library(mpi_abi SHARED ${ABIDIR}/mpi.c)
  set_target_properties(
    mpi_abi PROPERTIES
    SOVERSION 1
    MACHO_COMPATIBILITY_VERSION 0
    MACHO_CURRENT_VERSION 0
  )
  if(NOT TARGET MPI::MPI_C)
    add_library(MPI::MPI_C INTERFACE IMPORTED)
  endif()
  target_include_directories(MPI::MPI_C INTERFACE ${ABIDIR})
  target_link_libraries(MPI::MPI_C INTERFACE mpi_abi)
  set(MPIABI FORCE TRUE)
endif()


# Cython
set(cythonize ${TOPDIR}/conf/cythonize.py)
set(Cython_COMMAND ${Python_EXECUTABLE} ${cythonize})
set(Cython_OPTIONS --3str --cleanup 3)
set(MPI.pyx ${SRCDIR}/mpi4py/MPI.pyx)
file(
  GLOB_RECURSE MPI.deps
  ${SRCDIR}/mpi4py/*.pyx
  ${SRCDIR}/mpi4py/*.pxd
  ${SRCDIR}/mpi4py/MPI.src/*.pyx
  ${SRCDIR}/mpi4py/MPI.src/*.pxi
)
set(MPI.c ${BINDIR}/MPI.c)
set(MPI.h ${BINDIR}/MPI.h ${BINDIR}/MPI_api.h)
add_custom_command(
  OUTPUT ${MPI.c}
  BYPRODUCTS ${MPI.h}
  DEPENDS ${MPI.deps}
  WORKING_DIRECTORY ${TOPDIR}
  VERBATIM
  COMMAND
  ${Cython_COMMAND} ${Cython_OPTIONS}
  ${MPI.pyx} --output-file ${MPI.c}
)
install(FILES ${MPI.h} DESTINATION mpi4py)


# mpi4py.MPI
python_add_library(mpi4py.MPI MODULE ${MPI.c} WITH_SOABI ${WITH_SABI})
set_target_properties(mpi4py.MPI PROPERTIES OUTPUT_NAME "MPI" PREFIX "")
target_compile_definitions(mpi4py.MPI PRIVATE $<$<BOOL:${MPIABI}>:PYMPIABI=1>)
target_include_directories(mpi4py.MPI PRIVATE ${SRCDIR})
target_link_libraries(mpi4py.MPI PRIVATE MPI::MPI_C)
install(TARGETS mpi4py.MPI LIBRARY DESTINATION mpi4py)


# mpi4py/bin/python-mpi
if (Python_Development.Embed_FOUND)
add_executable(python-mpi ${SRCDIR}/python.c)
target_link_libraries(python-mpi PRIVATE Python::Python)
target_link_libraries(python-mpi PRIVATE MPI::MPI_C)
install(TARGETS python-mpi RUNTIME DESTINATION mpi4py/bin)
endif()


# mpi4py/*
file(
  GLOB mpi4py_SOURCES
  RELATIVE ${SRCDIR}
  ${SRCDIR}/mpi4py/*.py
  ${SRCDIR}/mpi4py/futures/*.py
  ${SRCDIR}/mpi4py/util/*.py
)
file(
  GLOB mpi4py_HEADERS
  RELATIVE ${SRCDIR}
  ${SRCDIR}/mpi4py/*.pxd
  ${SRCDIR}/mpi4py/include/mpi4py/*.[hi]
  ${SRCDIR}/mpi4py/include/mpi4py/*.px[di]
)
if (TRUE)
  list(APPEND mpi4py_HEADERS mpi4py/py.typed)
  list(APPEND mpi4py_HEADERS mpi4py/MPI.pyi)
  foreach(file ${mpi4py_SOURCES})
    list(APPEND mpi4py_HEADERS ${file}i)
  endforeach()
endif()
foreach(file ${mpi4py_SOURCES} ${mpi4py_HEADERS})
  get_filename_component(dir ${file} DIRECTORY)
  install(FILES ${SRCDIR}/${file} DESTINATION ${dir})
endforeach()

if (WIN32)
  set(mpidllpath _mpi_dll_path.py mpi.pth mpi.start)
  foreach(file ${mpidllpath})
    if (EXISTS ${SRCDIR}/${file})
      install(FILES ${SRCDIR}/${file} DESTINATION .)
    endif()
  endforeach()
endif()
