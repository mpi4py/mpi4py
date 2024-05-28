#include <mpi.h>
#include <iostream>

static void sayhello(MPI_Comm comm)
{
  if (comm == MPI_COMM_NULL) {
    std::cout << "You passed MPI_COMM_NULL !!!" << std::endl;
    return;
  }
  int size;
  MPI_Comm_size(comm, &size);
  int rank;
  MPI_Comm_rank(comm, &rank);
  int plen; char pname[MPI_MAX_PROCESSOR_NAME];
  MPI_Get_processor_name(pname, &plen);
  std::cout <<
    "Hello, World! " <<
    "I am process "  << rank  <<
    " of "           << size  <<
    " on  "          << pname <<
    "."              << std::endl;
}

#include <pybind11/pybind11.h>
#define MPI4PY_LIMITED_API 1
#define MPI4PY_LIMITED_API_SKIP_MESSAGE 1
#define MPI4PY_LIMITED_API_SKIP_SESSION 1
#include <mpi4py/mpi4py.h>
namespace py = pybind11;

template<typename T> T py2mpi(py::object);
template<> MPI_Comm py2mpi(py::object obj)
{
  PyObject *pyobj = obj.ptr();
  MPI_Comm *mpi_ptr = PyMPIComm_Get(pyobj);
  if (!mpi_ptr) throw py::error_already_set();
  return *mpi_ptr;
}

static void hw_sayhello(py::object py_comm)
{
  MPI_Comm comm = py2mpi<MPI_Comm>(py_comm);
  sayhello(comm);
}

PYBIND11_MODULE(helloworld, m) {

  if (import_mpi4py() < 0)
    throw py::error_already_set();

  m.def("sayhello", &hw_sayhello);
}

/*
 * Local Variables:
 * mode: C++
 * End:
 */
