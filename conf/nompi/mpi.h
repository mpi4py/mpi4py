/* Author:  Lisandro Dalcin   */
/* Contact: dalcinl@gmail.com */

#ifndef PyMPI_NOMPI_H
#define PyMPI_NOMPI_H

#define MPI_Init(a,b) ((void)a,(void)b,0)
#define MPI_Finalize() (0)
#define MPI_Initialized(a) ((*(a)=1),0)
#define MPI_Finalized(a) ((*(a)=1),0)

#define MPI_COMM_WORLD ((void*)0)
#define MPI_Comm_size(a,b) ((void)(a),(*(b)=1),0)
#define MPI_Comm_rank(a,b) ((void)(a),(*(b)=0),0)
#define MPI_Abort(a,b) ((void)(a),(void)(b),0)

#endif
