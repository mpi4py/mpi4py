cmake_minimum_required(VERSION 3.12.0)
project(mpi4py C)

find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)
find_package(MPI REQUIRED)

set(BINDIR ${CMAKE_CURRENT_BINARY_DIR})
set(PKGDIR ${CMAKE_CURRENT_SOURCE_DIR})
get_filename_component(SRCDIR ${PKGDIR} DIRECTORY)
get_filename_component(TOPDIR ${SRCDIR} DIRECTORY)
set(SKBUILD "${SKBUILD}")


# intelmpi.pth
include(CheckSymbolExists)
set(CMAKE_REQUIRED_INCLUDES ${MPI_C_INCLUDE_PATH})
check_symbol_exists(I_MPI_VERSION "mpi.h" HAVE_I_MPI_VERSION)
if (HAVE_I_MPI_VERSION AND WIN32)
  set(intelmpi.pth "${BINDIR}/intelmpi.pth")
  configure_file(${TOPDIR}/conf/intelmpi.pth ${intelmpi.pth} COPYONLY)
  install(FILES ${intelmpi.pth} DESTINATION src)
endif()


# mpi4py/mpi.cfg
set(mpi.cfg "${BINDIR}/mpi.cfg")
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
install(FILES ${mpi.cfg} DESTINATION src/mpi4py)


# Cython
set(cythonize ${TOPDIR}/conf/cythonize.py)
set(CYTHON_EXECUTABLE ${PYTHON_EXECUTABLE} ${cythonize})
set(CYTHON_FLAGS --working ${SRCDIR})
add_cython_target(MPI MPI.pyx OUTPUT_VAR MPI.c PY3)
file(GLOB_RECURSE MPI.pyx ${PKGDIR}/MPI/*.pyx ${PKGDIR}/MPI/*.pxi)
foreach(file MPI.h MPI_api.h)
  set(MPI.h ${MPI.h} ${BINDIR}/${file})
endforeach()
add_custom_command(
  OUTPUT ${MPI.c}
  DEPENDS ${MPI.pyx}
  BYPRODUCTS ${MPI.h}
  APPEND
)
install(FILES ${MPI.h} DESTINATION src/mpi4py)


# mpi4py.MPI
add_library(MPI MODULE ${MPI.c})
target_include_directories(MPI PRIVATE ${SRCDIR})
target_include_directories(MPI PRIVATE ${MPI_C_INCLUDE_PATH})
target_compile_definitions(MPI PRIVATE MPICH_SKIP_MPICXX=1)
target_compile_definitions(MPI PRIVATE OMPI_SKIP_MPICXX=1)
target_compile_definitions(MPI PRIVATE OMPI_WANT_MPI_INTERFACE_WARNING=0)
target_link_libraries(MPI ${MPI_C_LIBRARIES})
python_extension_module(MPI)
install(TARGETS MPI LIBRARY DESTINATION src/mpi4py)


# mpi4py/bin/python-mpi
add_executable(python-mpi ${SRCDIR}/python.c)
target_include_directories(python-mpi PRIVATE ${MPI_C_INCLUDE_PATH})
target_link_libraries(python-mpi ${MPI_C_LIBRARIES})
python_standalone_executable(python-mpi)
install(TARGETS python-mpi RUNTIME DESTINATION src/mpi4py/bin)
