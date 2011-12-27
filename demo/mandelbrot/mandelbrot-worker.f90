! $ mpif90 -o mandelbrot.exe mandelbrot.f90

program main

  use MPI
  implicit none

  integer master, nprocs, myrank, ierr

  real    :: rmsg(4), x1, x2, y1, y2
  integer :: imsg(3), w, h, maxit

  integer              :: N
  integer, allocatable :: I(:)
  integer, allocatable :: C(:,:)
  integer :: j, k
  real    :: x, dx, y, dy

  call MPI_Init(ierr)
  call MPI_Comm_get_parent(master, ierr)
  if (master == MPI_COMM_NULL) then
     print *, "parent communicator is MPI_COMM_NULL"
     call MPI_Abort(MPI_COMM_WORLD, 1, ierr)
  end if
  call MPI_Comm_size(master, nprocs, ierr)
  call MPI_Comm_rank(master, myrank, ierr)

  ! receive parameters and unpack
  call MPI_Bcast(rmsg, 4, MPI_REAL,    0, master, ierr)
  call MPI_Bcast(imsg, 3, MPI_INTEGER, 0, master, ierr)
  x1 = rmsg(1); x2 = rmsg(2)
  y1 = rmsg(3); y2 = rmsg(4)
  w = imsg(1); h = imsg(2); maxit = imsg(3)
  dx = (x2-x1)/real(w)
  dy = (y2-y1)/real(h)

  ! number of lines to compute here
  N = h / nprocs
  if (modulo(h, nprocs) > myrank) then
     N = N + 1
  end if

  ! indices of lines to compute here
  allocate( I(0:N-1) )
  I = (/ (k, k=myrank, h-1, nprocs) /)

  ! compute local lines
  allocate( C(0:w-1, 0:N-1) )
  do k = 0, N-1
     y = y1 + real(I(k)) * dy
     do j = 0, w-1
        x = x1 + real(j) * dx
        C(j, k) = mandelbrot(x, y, maxit)
     end do
  end do

  ! send number of lines computed here
  call MPI_Gather(N, 1, MPI_INTEGER, &
                  MPI_BOTTOM, 0, MPI_BYTE, &
                  0, master, ierr)

  ! send indices of lines computed here
  call MPI_Gatherv(I, N, MPI_INTEGER, &
                   MPI_BOTTOM, MPI_BOTTOM, MPI_BOTTOM, MPI_BYTE, &
                   0, master, ierr)

  ! send data of lines computed here
  call MPI_Gatherv(C, N*w, MPI_INTEGER, &
                   MPI_BOTTOM, MPI_BOTTOM, MPI_BOTTOM, MPI_BYTE, &
                   0, master, ierr)

  deallocate(C)
  deallocate(I)

  ! we are done
  call MPI_Comm_disconnect(master, ierr)
  call MPI_Finalize(ierr)

contains

  function mandelbrot(x, y, maxit) result (it)
    implicit none
    real,    intent(in) :: x, y
    integer, intent(in) :: maxit
    integer :: it
    complex :: z, c
    z = cmplx(0, 0)
    c = cmplx(x, y)
    it = 0
    do while (abs(z) < 2.0 .and. it < maxit)
       z = z*z + c
       it = it + 1
    end do
  end function mandelbrot

end program main
