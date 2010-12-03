# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

PROJECT(mpi4py)

FIND_PACKAGE(PythonInterp)
FIND_PACKAGE(PythonLibs)
FIND_PACKAGE(MPI)

SET(mpi4py_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")
SET(mpi4py_BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/mpi4py")

SET(mpi4py_PYTHON_FILES
  __init__.py
  rc.py
  )
SET(mpi4py_HEADER_FILES
  include/mpi4py/__init__.pxd
  include/mpi4py/__init__.pyx
  include/mpi4py/MPI.pxd
  include/mpi4py/mpi.pxi
  include/mpi4py/mpi_c.pxd
  include/mpi4py/mpi4py.h
  include/mpi4py/mpi4py.MPI.h
  include/mpi4py/mpi4py.MPI_api.h
  include/mpi4py/mpi4py.i
  )

FOREACH(file
        ${mpi4py_PYTHON_FILES}
        ${mpi4py_HEADER_FILES}
        )
  SET(src "${mpi4py_SOURCE_DIR}/${file}")
  SET(tgt "${mpi4py_BINARY_DIR}/${file}")
  ADD_CUSTOM_COMMAND(
    DEPENDS ${src}
    OUTPUT  ${tgt}
    COMMAND ${CMAKE_COMMAND} ARGS -E copy ${src} ${tgt}
    COMMENT "copy: ${file}"
    )
  SET(mpi4py_OUTPUT_FILES ${mpi4py_OUTPUT_FILES} ${tgt})
ENDFOREACH(file)


FOREACH(file ${mpi4py_PYTHON_FILES})
  SET(mpi4py_py  ${mpi4py_py}  "${mpi4py_BINARY_DIR}/${file}")
  SET(mpi4py_pyc ${mpi4py_pyc} "${mpi4py_BINARY_DIR}/${file}c")
  SET(mpi4py_pyo ${mpi4py_pyo} "${mpi4py_BINARY_DIR}/${file}o")
ENDFOREACH(file)
ADD_CUSTOM_COMMAND(
  COMMAND ${CMAKE_COMMAND} ARGS -E echo 'from compileall import compile_dir'     > compile_py
  COMMAND ${CMAKE_COMMAND} ARGS -E echo 'compile_dir(\"${mpi4py_BINARY_DIR}\")' >> "compile_py"
  COMMAND ${PYTHON_EXECUTABLE} ARGS compile_py
  COMMAND ${PYTHON_EXECUTABLE} ARGS -O compile_py
  COMMAND ${CMAKE_COMMAND} ARGS -E remove compile_py
  DEPENDS ${mpi4py_py}
  OUTPUT  ${mpi4py_pyc} ${mpi4py_pyo}
  )
SET(mpi4py_OUTPUT_FILES ${mpi4py_OUTPUT_FILES} ${mpi4py_pyc} ${mpi4py_pyo})


FIND_PROGRAM(MPI_COMPILER_CC
  NAMES mpicc
  HINTS "${MPI_BASE_DIR}"
  PATH_SUFFIXES bin
  DOC "MPI C compiler wrapper")
MARK_AS_ADVANCED(MPI_COMPILER_CC)
FIND_PROGRAM(MPI_COMPILER_CXX
  NAMES mpicxx mpic++ mpiCC
  HINTS "${MPI_BASE_DIR}"
  PATH_SUFFIXES bin
  DOC "MPI C++ compiler wrapper")
MARK_AS_ADVANCED(MPI_COMPILER_CXX)
find_program(MPI_COMPILER_F77
  NAMES mpif77
  HINTS "${MPI_BASE_DIR}"
  PATH_SUFFIXES bin
  DOC "MPI F77 compiler wrapper")
MARK_AS_ADVANCED(MPI_COMPILER_F77)
FIND_PROGRAM(MPI_COMPILER_F90
  NAMES mpif90
  HINTS "${MPI_BASE_DIR}"
  PATH_SUFFIXES bin
  DOC "MPI F90 compiler wrapper")
MARK_AS_ADVANCED(MPI_COMPILER_F90)
FOREACH(file "mpi.cfg")
  SET(tgt "${mpi4py_BINARY_DIR}/${file}")
  ADD_CUSTOM_COMMAND(
    OUTPUT  ${tgt}
    COMMAND ${CMAKE_COMMAND} ARGS -E echo '[mpi]' > "${tgt}"
    COMMAND ${CMAKE_COMMAND} ARGS -E echo 'mpicc  = ${MPI_COMPILER_CC}'  >> ${tgt}
    COMMAND ${CMAKE_COMMAND} ARGS -E echo 'mpicxx = ${MPI_COMPILER_CXX}' >> ${tgt}
    COMMAND ${CMAKE_COMMAND} ARGS -E echo 'mpif77 = ${MPI_COMPILER_F77}' >> ${tgt}
    COMMAND ${CMAKE_COMMAND} ARGS -E echo 'mpif90 = ${MPI_COMPILER_F90}' >> ${tgt}
    COMMENT "write: ${file}"
    )
  SET(mpi4py_OUTPUT_FILES ${mpi4py_OUTPUT_FILES} ${tgt})
ENDFOREACH(file)

ADD_CUSTOM_TARGET(mpi4py ALL DEPENDS ${mpi4py_OUTPUT_FILES})

INCLUDE_DIRECTORIES(
  ${MPI_INCLUDE_PATH}
  ${PYTHON_INCLUDE_PATH}
  "${mpi4py_SOURCE_DIR}"
  )

# --- mpi4py.MPI ---
PYTHON_ADD_MODULE(mpi4py.MPI MODULE "${mpi4py_SOURCE_DIR}/MPI.c")
SET_TARGET_PROPERTIES(
  mpi4py.MPI PROPERTIES
  OUTPUT_NAME "MPI" PREFIX ""
  COMPILE_FLAGS "${MPI_COMPILE_FLAGS}"
  LINK_FLAGS "${MPI_LINK_FLAGS}"
  LIBRARY_OUTPUT_DIRECTORY "${mpi4py_BINARY_DIR}"
  RUNTIME_OUTPUT_DIRECTORY "${mpi4py_BINARY_DIR}"
  LINKER_LANGUAGE C
)
TARGET_LINK_LIBRARIES(mpi4py.MPI ${PYTHON_LIBRARY})
TARGET_LINK_LIBRARIES(mpi4py.MPI ${MPI_LIBRARIES})


# --- mpi4py.MPE ---
PYTHON_ADD_MODULE(mpi4py.MPE MODULE ${mpi4py_SOURCE_DIR}/MPE.c)
SET_TARGET_PROPERTIES(
  mpi4py.MPE PROPERTIES
  OUTPUT_NAME "MPE" PREFIX ""
  COMPILE_FLAGS "${MPE_COMPILE_FLAGS}" "${MPI_COMPILE_FLAGS}"
  LINK_FLAGS "${MPE_LINK_FLAGS}" "${MPI_LINK_FLAGS}"
  LIBRARY_OUTPUT_DIRECTORY ${mpi4py_BINARY_DIR}
  RUNTIME_OUTPUT_DIRECTORY ${mpi4py_BINARY_DIR}
  LINKER_LANGUAGE C
)
TARGET_LINK_LIBRARIES(mpi4py.MPE ${PYTHON_LIBRARY})
TARGET_LINK_LIBRARIES(mpi4py.MPE ${MPE_LIBRARY})
TARGET_LINK_LIBRARIES(mpi4py.MPE ${MPI_LIBRARIES})


# --- mpi4py.dl ---
PYTHON_ADD_MODULE(mpi4py.dl MODULE "${mpi4py_SOURCE_DIR}/dynload.c")
SET_TARGET_PROPERTIES(
  mpi4py.dl PROPERTIES
  OUTPUT_NAME "dl" PREFIX ""
  LIBRARY_OUTPUT_DIRECTORY "${mpi4py_BINARY_DIR}"
  RUNTIME_OUTPUT_DIRECTORY "${mpi4py_BINARY_DIR}"
  LINKER_LANGUAGE C
)
TARGET_LINK_LIBRARIES(mpi4py.dl ${PYTHON_LIBRARY})
TARGET_LINK_LIBRARIES(mpi4py.dl ${CMAKE_DL_LIBS})
