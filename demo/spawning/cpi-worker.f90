PROGRAM main

  USE mpi
  implicit none

  integer ierr
  integer n, i, master, myrank, nprocs
  real (kind=8) h, s, x, cpi

  call MPI_INIT(ierr)
  call MPI_COMM_GET_PARENT(master, ierr)
  call MPI_COMM_SIZE(master, nprocs, ierr)
  call MPI_COMM_RANK(master, myrank, ierr)

  call MPI_BCAST(n, 1, MPI_INTEGER, &
                 0, master, ierr)

  h = 1 / DFLOAT(n)
  s = 0.0
  DO i=myrank+1,n,nprocs
     x = h * (DFLOAT(i) - 0.5)
     s = s +  4.0 / (1.0 + x*x)
  END DO
  cpi = s * h

  call MPI_REDUCE(cpi, MPI_BOTTOM, 1, MPI_DOUBLE_PRECISION, &
                  MPI_SUM, 0, master, ierr)

  call MPI_COMM_DISCONNECT(master, ierr)
  call MPI_FINALIZE(ierr)

END PROGRAM main
