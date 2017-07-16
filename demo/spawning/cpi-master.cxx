#include <mpi.h>
#include <cstdio>
#include <cstring>
#include <cmath>

int main(int argc, char *argv[])
{
  MPI::Init();

  char cmd[32] = "./cpi-worker-cxx.exe";
  if (argc > 1) std::strcpy(cmd, argv[1]);
  std::printf("%s -> %s\n", argv[0], cmd);

  MPI::Intercomm worker;
  worker = MPI::COMM_SELF.Spawn(cmd, MPI::ARGV_NULL, 5,
                                MPI::INFO_NULL, 0);

  int n = 100;
  worker.Bcast(&n, 1, MPI::INT, MPI::ROOT);

  double pi;
  worker.Reduce(MPI::BOTTOM, &pi, 1, MPI::DOUBLE,
                MPI::SUM, MPI::ROOT);

  worker.Disconnect();

  std::printf("pi: %.16f, error: %.16f\n", pi, std::fabs(M_PI-pi));

  MPI::Finalize();
  return 0;
}
