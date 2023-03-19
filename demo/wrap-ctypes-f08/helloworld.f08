subroutine sayhello(comm) bind(C)
  use mpi_f08
  implicit none
  type(MPI_Comm), intent(in) :: comm

  integer :: rank, size, nlen
  character (len=MPI_MAX_PROCESSOR_NAME) :: name

  if (comm == MPI_COMM_NULL) then
     print*, "You passed MPI_COMM_NULL !!!"
     return
  end if

  call MPI_Comm_rank(comm, rank)
  call MPI_Comm_size(comm, size)
  call MPI_Get_processor_name(name, nlen)

  print '(2A,I2,A,I2,3A)', &
       'Hello, World!', &
       ' I am process ', rank, &
       ' of ', size, &
       ' on ', name(1:nlen), '.'
  
end subroutine sayhello
