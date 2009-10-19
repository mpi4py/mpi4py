#include <mpi.h>
#include <iostream>

int main(int argc, char *argv[])
{
#if defined(MPI_VERSION) && (MPI_VERSION >= 2)
  MPI::Init_thread(MPI_THREAD_MULTIPLE);
#else
  MPI::Init();
#endif

  int size = MPI::COMM_WORLD.Get_size();
  int rank = MPI::COMM_WORLD.Get_rank();
  int len; char name[MPI_MAX_PROCESSOR_NAME];
  MPI::Get_processor_name(name, len);

  std::cout <<
    "Hello, World! " <<
    "I am process "  << rank <<
    " of "           << size <<
    " on  "          << name <<
    "."              << std::endl;

  MPI::Finalize();
  return 0;
}

// Local Variables:
// mode: C++
// c-basic-offset: 2
// indent-tabs-mode: nil
// End:
