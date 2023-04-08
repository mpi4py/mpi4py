cmake_minimum_required(VERSION 3.18.0...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

find_package(
  Python REQUIRED
  COMPONENTS Interpreter
  COMPONENTS Development.Module
  OPTIONAL_COMPONENTS Development.Embed
)
find_package(
  MPI REQUIRED
)

set(BINDIR ${CMAKE_CURRENT_BINARY_DIR})
set(PKGDIR ${CMAKE_CURRENT_SOURCE_DIR})
get_filename_component(SRCDIR ${PKGDIR} DIRECTORY)
get_filename_component(TOPDIR ${SRCDIR} DIRECTORY)


# intelmpi.pth
include(CheckSymbolExists)
set(CMAKE_REQUIRED_INCLUDES ${MPI_C_INCLUDE_PATH})
check_symbol_exists(I_MPI_VERSION "mpi.h" HAVE_I_MPI_VERSION)
if (HAVE_I_MPI_VERSION AND WIN32)
  set(intelmpi.pth "${BINDIR}/intelmpi.pth")
  configure_file(${TOPDIR}/conf/intelmpi.pth ${intelmpi.pth} COPYONLY)
  install(FILES ${intelmpi.pth} DESTINATION .)
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
install(FILES ${mpi.cfg} DESTINATION ${SKBUILD_PROJECT_NAME})


# Cython
set(cythonize ${TOPDIR}/conf/cythonize.py)
set(Cython_COMMAND ${Python_EXECUTABLE} ${cythonize})
set(Cython_OPTIONS -3 --cleanup 3)
set(MPI.pyx ${PKGDIR}/MPI.pyx)
file(
  GLOB_RECURSE MPI.deps
  ${PKGDIR}/*.pyx ${PKGDIR}/*.pxd
  ${PKGDIR}/MPI/*.pyx ${PKGDIR}/MPI/*.pxi
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
  --working ${SRCDIR} ${MPI.pyx} --output-file ${MPI.c}
)
install(FILES ${MPI.h} DESTINATION ${SKBUILD_PROJECT_NAME})


# mpi4py.MPI
python_add_library(mpi4py.MPI MODULE ${MPI.c} WITH_SOABI)
set_target_properties(mpi4py.MPI PROPERTIES OUTPUT_NAME "MPI" PREFIX "")
target_include_directories(mpi4py.MPI PRIVATE ${SRCDIR})
target_include_directories(mpi4py.MPI PRIVATE ${MPI_C_INCLUDE_DIRS})
target_link_directories(mpi4py.MPI PRIVATE ${MPI_C_LIBRARY_DIRS})
target_link_libraries(mpi4py.MPI PRIVATE ${MPI_C_LIBRARIES})
install(TARGETS mpi4py.MPI LIBRARY DESTINATION ${SKBUILD_PROJECT_NAME})


# mpi4py/bin/python-mpi
if (Python_Development.Embed_FOUND)
add_executable(python-mpi ${SRCDIR}/python.c)
target_include_directories(python-mpi PRIVATE ${Python_INCLUDE_DIRS})
target_link_directories(python-mpi PRIVATE ${Python_LIBRARY_DIRS})
target_link_libraries(python-mpi PRIVATE ${Python_LIBRARIES})
target_include_directories(python-mpi PRIVATE ${MPI_C_INCLUDE_DIRS})
target_link_directories(python-mpi PRIVATE ${MPI_C_LIBRARY_DIRS})
target_link_libraries(python-mpi PRIVATE ${MPI_C_LIBRARIES})
install(TARGETS python-mpi RUNTIME DESTINATION ${SKBUILD_PROJECT_NAME}/bin)
endif()
