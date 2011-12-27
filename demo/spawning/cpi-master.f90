PROGRAM main

  USE mpi
  implicit none

  real (kind=8), parameter :: PI = 3.1415926535897931D0

  integer argc
  character(len=32) argv(0:1)

  character(len=32) cmd
  integer ierr, n, worker
  real(kind=8) cpi

  call MPI_INIT(ierr)

  argc = iargc() + 1
  call getarg(0, argv(0))
  call getarg(1, argv(1))

  cmd = 'cpi-worker-f90.exe'
  if (argc > 1) then
     cmd = argv(1)
  end if
  write(*,'(A,A,A)') trim(argv(0)), ' -> ', trim(cmd)

  call MPI_COMM_SPAWN(cmd, MPI_ARGV_NULL, 5, &
                      MPI_INFO_NULL, 0, &
                      MPI_COMM_SELF, worker, &
                      MPI_ERRCODES_IGNORE, ierr)

  n = 100
  call MPI_BCAST(n, 1, MPI_INTEGER, &
                 MPI_ROOT, worker, ierr)

  call MPI_REDUCE(MPI_BOTTOM, cpi, 1, MPI_DOUBLE_PRECISION, &
                  MPI_SUM, MPI_ROOT, worker, ierr)

  call MPI_COMM_DISCONNECT(worker, ierr)

  write(*,'(A,F18.16,A,F18.16)') 'pi: ', cpi, ', error: ', abs(PI-cpi)

  call MPI_FINALIZE(ierr)

END PROGRAM main
