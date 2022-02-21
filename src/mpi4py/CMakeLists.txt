cmake_minimum_required(VERSION 3.12.0)
project(mpi4py C)

find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)
find_package(MPI REQUIRED)

if(CMAKE_DL_LIBS)
  find_library(DL_LIBS ${CMAKE_DL_LIBS})
endif()
if(NOT DL_LIBS)
  set(DL_LIBS "")
endif()

set(BINDIR ${CMAKE_CURRENT_BINARY_DIR})
set(PKGDIR ${CMAKE_CURRENT_SOURCE_DIR})
get_filename_component(SRCDIR ${PKGDIR} DIRECTORY)
get_filename_component(TOPDIR ${SRCDIR} DIRECTORY)
set(SKBUILD "${SKBUILD}")


# mpi.cfg
set(mpi.cfg "${BINDIR}/mpi.cfg")
file(WRITE ${mpi.cfg} "[mpi]\n")
file(APPEND ${mpi.cfg} "mpicc = ${MPI_C_COMPILER}\n")
install(FILES ${mpi.cfg} DESTINATION src/mpi4py)


# Cython
set(cythoncmd ${TOPDIR}/conf/cythoncmd.py --cleanup 3)
set(CYTHON_EXECUTABLE ${PYTHON_EXECUTABLE} ${cythoncmd})
add_cython_target(mpi4py.MPI MPI.pyx OUTPUT_VAR mpi4py.MPI.c PY3)
file(GLOB_RECURSE mpi4py.MPI.pyx ${PKGDIR}/MPI/*.pyx ${PKGDIR}/MPI/*.pxi)
foreach(file mpi4py.MPI.h mpi4py.MPI_api.h)
  set(mpi4py.MPI.h ${mpi4py.MPI.h} ${BINDIR}/${file})
endforeach()
add_custom_command(
  OUTPUT ${mpi4py.MPI.c}
  DEPENDS ${mpi4py.MPI.pyx}
  BYPRODUCTS ${mpi4py.MPI.h}
  APPEND
  )
install(FILES ${mpi4py.MPI.h} DESTINATION src/mpi4py/include)


# mpi4py.MPI
add_library(MPI MODULE ${mpi4py.MPI.c})
target_include_directories(MPI PRIVATE ${SRCDIR})
target_include_directories(MPI PRIVATE ${MPI_C_INCLUDE_PATH})
target_compile_definitions(MPI PRIVATE MPICH_SKIP_MPICXX=1)
target_compile_definitions(MPI PRIVATE OMPI_SKIP_MPICXX=1)
target_compile_definitions(MPI PRIVATE OMPI_WANT_MPI_INTERFACE_WARNING=0)
target_link_libraries(MPI ${MPI_C_LIBRARIES})
python_extension_module(MPI)
install(TARGETS MPI LIBRARY DESTINATION src/mpi4py)


# mpi4py.dl
add_library(dl MODULE ${SRCDIR}/dynload.c)
target_link_libraries(dl ${DL_LIBS})
python_extension_module(dl)
install(TARGETS dl LIBRARY DESTINATION src/mpi4py)


# mpi4py/bin/python-mpi
add_executable(python-mpi ${SRCDIR}/python.c)
target_include_directories(python-mpi PRIVATE ${MPI_C_INCLUDE_PATH})
target_link_libraries(python-mpi ${MPI_C_LIBRARIES})
python_standalone_executable(python-mpi)
install(TARGETS python-mpi RUNTIME DESTINATION src/mpi4py/bin)
