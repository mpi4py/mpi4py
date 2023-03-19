subroutine sayhello(comm)
  use mpi
  implicit none
  integer, intent(in) :: comm

  integer :: rank, size, nlen, ierr
  character (len=MPI_MAX_PROCESSOR_NAME) :: name

  if (comm == MPI_COMM_NULL) then
     print*, 'You passed MPI_COMM_NULL !!!'
     return
  end if

  call MPI_Comm_rank(comm, rank, ierr)
  call MPI_Comm_size(comm, size, ierr)
  call MPI_Get_processor_name(name, nlen, ierr)

  print '(2A,I2,A,I2,3A)', &
       'Hello, World!', &
       ' I am process ', rank, &
       ' of ', size, &
       ' on ', name(1:nlen), '.'

end subroutine sayhello
