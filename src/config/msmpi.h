#ifndef PyMPI_CONFIG_MSMPI_H
#define PyMPI_CONFIG_MSMPI_H

#define PyMPI_API_CALL MPIAPI

#define PyMPI_MISSING_MPI_LOGICAL1 1
#define PyMPI_MISSING_MPI_LOGICAL2 1
#define PyMPI_MISSING_MPI_LOGICAL4 1
#define PyMPI_MISSING_MPI_LOGICAL8 1
#define PyMPI_MISSING_MPI_REAL2 1
#define PyMPI_MISSING_MPI_COMPLEX4 1

#if !defined(MPICH2_NUMVERSION) || (MPICH2_NUMVERSION < 10100000)
#define PyMPI_MISSING_MPI_Type_create_f90_integer 1
#define PyMPI_MISSING_MPI_Type_create_f90_real 1
#define PyMPI_MISSING_MPI_Type_create_f90_complex 1
#endif /* MPICH2 < 1.1.0 */

#define PyMPI_MISSING_MPI_Op_commutative 1
#define PyMPI_MISSING_MPI_Reduce_local 1
#define PyMPI_MISSING_MPI_Reduce_scatter_block 1

#define PyMPI_MISSING_MPI_DIST_GRAPH 1
#define PyMPI_MISSING_MPI_UNWEIGHTED 1
#define PyMPI_MISSING_MPI_Dist_graph_create_adjacent 1
#define PyMPI_MISSING_MPI_Dist_graph_create 1
#define PyMPI_MISSING_MPI_Dist_graph_neighbors_count 1
#define PyMPI_MISSING_MPI_Dist_graph_neighbors 1

#define PyMPI_MISSING_MPI_File_c2f 1
#define PyMPI_MISSING_MPI_File_f2c 1

#endif /* !PyMPI_CONFIG_MSMPI_H */
