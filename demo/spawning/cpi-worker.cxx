#include <mpi.h>

int main(int argc, char *argv[])
{
  MPI::Init();

  MPI::Intercomm master = MPI::Comm::Get_parent();
  int nprocs = master.Get_size();
  int myrank = master.Get_rank();

  int n;
  master.Bcast(&n, 1, MPI_INT, 0);

  double h = 1.0 / (double) n;
  double s = 0.0;
  for (int i = myrank+1; i < n+1; i += nprocs) {
    double x = h * (i - 0.5);
    s += 4.0 / (1.0 + x*x);
  }
  double pi = s * h;

  master.Reduce(&pi, MPI_BOTTOM, 1, MPI_DOUBLE,
                MPI_SUM, 0);

  master.Disconnect();

  MPI::Finalize();
  return 0;
}
