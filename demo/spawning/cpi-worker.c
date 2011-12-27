#include <mpi.h>

int main(int argc, char *argv[])
{
  int myrank, nprocs;
  int n, i;
  double h, s, pi;
  MPI_Comm master;

  MPI_Init(&argc, &argv);

  MPI_Comm_get_parent(&master);
  MPI_Comm_size(master, &nprocs);
  MPI_Comm_rank(master, &myrank);

  MPI_Bcast(&n, 1, MPI_INT, 0, master);

  h = 1.0 / (double) n;
  s = 0.0;
  for (i = myrank+1; i < n+1; i += nprocs) {
    double x = h * (i - 0.5);
    s += 4.0 / (1.0 + x*x);
  }
  pi = s * h;

  MPI_Reduce(&pi, MPI_BOTTOM, 1, MPI_DOUBLE,
             MPI_SUM, 0, master);

  MPI_Comm_disconnect(&master);

  MPI_Finalize();
  return 0;
}
