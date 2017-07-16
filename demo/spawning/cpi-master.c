#include <mpi.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

int main(int argc, char *argv[])
{
  char cmd[32] = "./cpi-worker-c.exe";
  MPI_Comm worker;
  int n;
  double pi;

  MPI_Init(&argc, &argv);

  if (argc > 1) strcpy(cmd, argv[1]);
  printf("%s -> %s\n", argv[0], cmd);

  MPI_Comm_spawn(cmd, MPI_ARGV_NULL, 5,
                 MPI_INFO_NULL, 0,
                 MPI_COMM_SELF, &worker,
                 MPI_ERRCODES_IGNORE);

  n = 100;
  MPI_Bcast(&n, 1, MPI_INT, MPI_ROOT, worker);

  MPI_Reduce(MPI_BOTTOM, &pi, 1, MPI_DOUBLE,
             MPI_SUM, MPI_ROOT, worker);

  MPI_Comm_disconnect(&worker);

  printf("pi: %.16f, error: %.16f\n", pi, fabs(M_PI-pi));

  MPI_Finalize();
  return 0;
}
