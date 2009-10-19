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


#include <boost/python.hpp>
#include <mpi4py/mpi4py.h>
using namespace boost::python;

static void hw_sayhello(object py_comm)
{
  PyObject* py_obj = py_comm.ptr();
  MPI_Comm *comm_p = PyMPIComm_Get(py_obj);
  if (comm_p == NULL) throw_error_already_set();
  sayhello(*comm_p);
}

BOOST_PYTHON_MODULE(helloworld)
{
  if (import_mpi4py() < 0) return; /* Python 2.X */

  def("sayhello", hw_sayhello);
}


/*
 * Local Variables:
 * mode: C++
 * End:
 */
