/*
This code is adapted from Jeff Hammond's BigMPI.
https://github.com/jeffhammond/BigMPI

The MIT License (MIT)

Copyright (c) 2013, 2014 Argonne National Laboratory
Copyright (c) 2014       Friedrich-Alexander-Universitaet Erlangen-Nuernberg
Copyright (c) 2014       Intel Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

#include <stdint.h>
#include <limits.h>

#define BIGMPI_COUNT_MAX (SIZE_MAX)
#define BIGMPI_INT_MAX (INT_MAX)
#if ( defined(__GNUC__) && (__GNUC__ >= 3) ) || defined(__IBMC__) || defined(__INTEL_COMPILER) || defined(__clang__)
#  define bmpi_unlikely(x_) __builtin_expect(!!(x_),0)
#  define bmpi_likely(x_)   __builtin_expect(!!(x_),1)
#else
#  define bmpi_unlikely(x_) (x_)
#  define bmpi_likely(x_)   (x_)
#endif

static int BigMPI_Type_contiguous(MPI_Aint offset, MPI_Count count, MPI_Datatype oldtype, MPI_Datatype * newtype)
{
    /* The count has to fit into MPI_Aint for BigMPI to work. */
    if ((uint64_t)count>(uint64_t)BIGMPI_COUNT_MAX) {
        return MPI_ERR_COUNT;
    }

    MPI_Count c = count/BIGMPI_INT_MAX;
    MPI_Count r = count%BIGMPI_INT_MAX;


    if(c>=BIGMPI_INT_MAX || r>=BIGMPI_INT_MAX){
        return MPI_ERR_COUNT;
    }

    MPI_Datatype chunks;
    MPI_Type_vector(c, BIGMPI_INT_MAX, BIGMPI_INT_MAX, oldtype, &chunks);

    MPI_Datatype remainder;
    MPI_Type_contiguous(r, oldtype, &remainder);

    MPI_Aint lb /* unused */, extent;
    MPI_Type_get_extent(oldtype, &lb, &extent);

    MPI_Aint remdisp          = (MPI_Aint)c*BIGMPI_INT_MAX*extent;
    int blocklengths[2]       = {1,1};
    MPI_Aint displacements[2] = {offset,offset+remdisp};
    MPI_Datatype types[2]     = {chunks,remainder};
    MPI_Type_create_struct(2, blocklengths, displacements, types, newtype);

    MPI_Type_free(&chunks);
    MPI_Type_free(&remainder);

    return MPI_SUCCESS;
}

static int MPIX_Type_contiguous_x(MPI_Count count, MPI_Datatype oldtype, MPI_Datatype * newtype)
{
    return BigMPI_Type_contiguous(0, count, oldtype, newtype);
}


static int MPIX_Send_x(void *buf, MPI_Count count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Send(buf, (int)count, datatype, dest, tag, comm);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Send(buf, 1, newtype, dest, tag, comm);
        MPI_Type_free(&newtype);
    }
    return rc;
}

static int MPIX_Recv_x(void *buf, MPI_Count count, MPI_Datatype datatype, int source, int tag, MPI_Comm comm, MPI_Status *status)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Recv(buf, (int)count, datatype, source, tag, comm, status);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Recv(buf, 1, newtype, source, tag, comm, status);
        MPI_Type_free(&newtype);
    }
    return rc;
}

static int MPIX_Isend_x(void *buf, MPI_Count count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm, MPI_Request * request)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Isend(buf, (int)count, datatype, dest, tag, comm, request);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Isend(buf, 1, newtype, dest, tag, comm, request);
        MPI_Type_free(&newtype);
    }
    return rc;
}

static int MPIX_Irecv_x(void *buf, MPI_Count count, MPI_Datatype datatype, int source, int tag, MPI_Comm comm, MPI_Request * request)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Irecv(buf, (int)count, datatype, source, tag, comm, request);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Irecv(buf, 1, newtype, source, tag, comm, request);
        MPI_Type_free(&newtype);
    }
    return rc;
}

static int MPIX_Sendrecv_x(void *sendbuf, MPI_Count sendcount, MPI_Datatype sendtype, int dest, int sendtag,
                    void *recvbuf, MPI_Count recvcount, MPI_Datatype recvtype, int source, int recvtag,
                    MPI_Comm comm, MPI_Status *status)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (sendcount <= BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX )) {
        rc = MPI_Sendrecv(sendbuf, (int)sendcount, sendtype, dest, sendtag,
                          recvbuf, (int)recvcount, recvtype, source, recvtag,
                          comm, status);
    } else if (sendcount <= BIGMPI_INT_MAX && recvcount > BIGMPI_INT_MAX ) {
        MPI_Datatype newrecvtype;
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Sendrecv(sendbuf, (int)sendcount, sendtype, dest, sendtag,
                          recvbuf, 1, newrecvtype, source, recvtag,
                          comm, status);
        MPI_Type_free(&newrecvtype);
    } else if (sendcount > BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX ) {
        MPI_Datatype newsendtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        MPI_Type_commit(&newsendtype);
        rc = MPI_Sendrecv(sendbuf, 1, newsendtype, dest, sendtag,
                          recvbuf, (int)recvcount, recvtype, source, recvtag,
                          comm, status);
        MPI_Type_free(&newsendtype);
    } else {
        MPI_Datatype newsendtype, newrecvtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newsendtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Sendrecv(sendbuf, 1, newsendtype, dest, sendtag,
                          recvbuf, 1, newrecvtype, source, recvtag,
                          comm, status);
        MPI_Type_free(&newsendtype);
        MPI_Type_free(&newrecvtype);
    }
    return rc;
}

static int MPIX_Sendrecv_replace_x(void *buf, MPI_Count count, MPI_Datatype datatype, int dest, int sendtag,
                            int source, int recvtag, MPI_Comm comm, MPI_Status *status)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Sendrecv_replace(buf, (int)count, datatype, dest, sendtag, source, recvtag, comm, status);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Sendrecv_replace(buf, 1, newtype, dest, sendtag, source, recvtag, comm, status);
        MPI_Type_free(&newtype);
    }
    return rc;
}

static int MPIX_Isendrecv_x(void *sendbuf, MPI_Count sendcount, MPI_Datatype sendtype, int dest, int sendtag,
                    void *recvbuf, MPI_Count recvcount, MPI_Datatype recvtype, int source, int recvtag,
                    MPI_Comm comm, MPI_Request *request) {
    int rc = MPI_SUCCESS;

    if (bmpi_likely (sendcount <= BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX )) {
        rc = MPI_Isendrecv(sendbuf, (int)sendcount, sendtype, dest, sendtag,
                          recvbuf, (int)recvcount, recvtype, source, recvtag,
                          comm, request);
    } else if (sendcount <= BIGMPI_INT_MAX && recvcount > BIGMPI_INT_MAX ) {
        MPI_Datatype newrecvtype;
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Isendrecv(sendbuf, (int)sendcount, sendtype, dest, sendtag,
                          recvbuf, 1, newrecvtype, source, recvtag,
                          comm, request);
        MPI_Type_free(&newrecvtype);
    } else if (sendcount > BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX ) {
        MPI_Datatype newsendtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        MPI_Type_commit(&newsendtype);
        rc = MPI_Isendrecv(sendbuf, 1, newsendtype, dest, sendtag,
                          recvbuf, (int)recvcount, recvtype, source, recvtag,
                          comm, request);
        MPI_Type_free(&newsendtype);
    } else {
        MPI_Datatype newsendtype, newrecvtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newsendtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Isendrecv(sendbuf, 1, newsendtype, dest, sendtag,
                          recvbuf, 1, newrecvtype, source, recvtag,
                          comm, request);
        MPI_Type_free(&newsendtype);
        MPI_Type_free(&newrecvtype);
    }
    return rc;
}

static int MPIX_Isendrecv_replace_x(void *buf, MPI_Count count, MPI_Datatype datatype, int dest, int sendtag,
                            int source, int recvtag, MPI_Comm comm, MPI_Request *request)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Isendrecv_replace(buf, (int)count, datatype, dest, sendtag, source, recvtag, comm, request);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Isendrecv_replace(buf, 1, newtype, dest, sendtag, source, recvtag, comm, request);
        MPI_Type_free(&newtype);
    }
    return rc;
}


static int MPIX_Ssend_x(void *buf, MPI_Count count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Ssend(buf, (int)count, datatype, dest, tag, comm);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Ssend(buf, 1, newtype, dest, tag, comm);
        MPI_Type_free(&newtype);
    }
    return rc;
}

static int MPIX_Rsend_x(void *buf, MPI_Count count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Rsend(buf, (int)count, datatype, dest, tag, comm);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Rsend(buf, 1, newtype, dest, tag, comm);
        MPI_Type_free(&newtype);
    }
    return rc;
}

static int MPIX_Issend_x(void *buf, MPI_Count count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm, MPI_Request *request)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Issend(buf, (int)count, datatype, dest, tag, comm, request);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Issend(buf, 1, newtype, dest, tag, comm, request);
        MPI_Type_free(&newtype);
    }
    return rc;
}

static int MPIX_Irsend_x(void *buf, MPI_Count count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm, MPI_Request *request)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Irsend(buf, (int)count, datatype, dest, tag, comm, request);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Irsend(buf, 1, newtype, dest, tag, comm, request);
        MPI_Type_free(&newtype);
    }
    return rc;
}


static int MPIX_Bcast_x(void *buf, MPI_Count count, MPI_Datatype datatype, int root, MPI_Comm comm)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Bcast(buf, (int)count, datatype, root, comm);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Bcast(buf, 1, newtype, root, comm);
        MPI_Type_free(&newtype);
    }
    return rc;
}

static int MPIX_Gather_x(void *sendbuf, MPI_Count sendcount, MPI_Datatype sendtype,
                  void *recvbuf, MPI_Count recvcount, MPI_Datatype recvtype, int root, MPI_Comm comm)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (sendcount <= BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX )) {
        rc = MPI_Gather(sendbuf, (int)sendcount, sendtype, recvbuf, (int)recvcount, recvtype, root, comm);
    } else {
        MPI_Datatype newsendtype, newrecvtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newsendtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Gather(sendbuf, 1, newsendtype, recvbuf, 1, newrecvtype, root, comm);
        MPI_Type_free(&newsendtype);
        MPI_Type_free(&newrecvtype);
    }
    return rc;
}

static int MPIX_Scatter_x(void *sendbuf, MPI_Count sendcount, MPI_Datatype sendtype,
                   void *recvbuf, MPI_Count recvcount, MPI_Datatype recvtype, int root, MPI_Comm comm)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (sendcount <= BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX )) {
        rc = MPI_Scatter(sendbuf, (int)sendcount, sendtype, recvbuf, (int)recvcount, recvtype, root, comm);
    } else {
        MPI_Datatype newsendtype, newrecvtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newsendtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Scatter(sendbuf, 1, newsendtype, recvbuf, 1, newrecvtype, root, comm);
        MPI_Type_free(&newsendtype);
        MPI_Type_free(&newrecvtype);
    }
    return rc;
}

static int MPIX_Allgather_x(void *sendbuf, MPI_Count sendcount, MPI_Datatype sendtype,
                     void *recvbuf, MPI_Count recvcount, MPI_Datatype recvtype, MPI_Comm comm)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (sendcount <= BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX )) {
        rc = MPI_Allgather(sendbuf, (int)sendcount, sendtype, recvbuf, (int)recvcount, recvtype, comm);
    } else {
        MPI_Datatype newsendtype, newrecvtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newsendtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Allgather(sendbuf, 1, newsendtype, recvbuf, 1, newrecvtype, comm);
        MPI_Type_free(&newsendtype);
        MPI_Type_free(&newrecvtype);
    }
    return rc;
}

static int MPIX_Alltoall_x(void *sendbuf, MPI_Count sendcount, MPI_Datatype sendtype,
                    void *recvbuf, MPI_Count recvcount, MPI_Datatype recvtype, MPI_Comm comm)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (sendcount <= BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX )) {
        rc = MPI_Alltoall(sendbuf, (int)sendcount, sendtype, recvbuf, (int)recvcount, recvtype, comm);
    } else {
        MPI_Datatype newsendtype, newrecvtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newsendtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Alltoall(sendbuf, 1, newsendtype, recvbuf, 1, newrecvtype, comm);
        MPI_Type_free(&newsendtype);
        MPI_Type_free(&newrecvtype);
    }
    return rc;
}

static int MPIX_Ibcast_x(void *buf, MPI_Count count, MPI_Datatype datatype, int root, MPI_Comm comm, MPI_Request *request)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (count <= BIGMPI_INT_MAX )) {
        rc = MPI_Ibcast(buf, (int)count, datatype, root, comm, request);
    } else {
        MPI_Datatype newtype;
        BigMPI_Type_contiguous(0,count, datatype, &newtype);
        MPI_Type_commit(&newtype);
        rc = MPI_Ibcast(buf, 1, newtype, root, comm, request);
        MPI_Type_free(&newtype);
    }
    return rc;
}

static int MPIX_Igather_x(void *sendbuf, MPI_Count sendcount, MPI_Datatype sendtype,
                  void *recvbuf, MPI_Count recvcount, MPI_Datatype recvtype, int root, MPI_Comm comm, MPI_Request *request)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (sendcount <= BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX )) {
        rc = MPI_Igather(sendbuf, (int)sendcount, sendtype, recvbuf, (int)recvcount, recvtype, root, comm, request);
    } else {
        MPI_Datatype newsendtype, newrecvtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newsendtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Igather(sendbuf, 1, newsendtype, recvbuf, 1, newrecvtype, root, comm, request);
        MPI_Type_free(&newsendtype);
        MPI_Type_free(&newrecvtype);
    }
    return rc;
}

static int MPIX_Iscatter_x(void *sendbuf, MPI_Count sendcount, MPI_Datatype sendtype,
                   void *recvbuf, MPI_Count recvcount, MPI_Datatype recvtype, int root, MPI_Comm comm, MPI_Request *request)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (sendcount <= BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX )) {
        rc = MPI_Iscatter(sendbuf, (int)sendcount, sendtype, recvbuf, (int)recvcount, recvtype, root, comm, request);
    } else {
        MPI_Datatype newsendtype, newrecvtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newsendtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Iscatter(sendbuf, 1, newsendtype, recvbuf, 1, newrecvtype, root, comm, request);
        MPI_Type_free(&newsendtype);
        MPI_Type_free(&newrecvtype);
    }
    return rc;
}

static int MPIX_Iallgather_x(void *sendbuf, MPI_Count sendcount, MPI_Datatype sendtype,
                     void *recvbuf, MPI_Count recvcount, MPI_Datatype recvtype, MPI_Comm comm, MPI_Request *request)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (sendcount <= BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX )) {
        rc = MPI_Iallgather(sendbuf, (int)sendcount, sendtype, recvbuf, (int)recvcount, recvtype, comm, request);
    } else {
        MPI_Datatype newsendtype, newrecvtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newsendtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Iallgather(sendbuf, 1, newsendtype, recvbuf, 1, newrecvtype, comm, request);
        MPI_Type_free(&newsendtype);
        MPI_Type_free(&newrecvtype);
    }
    return rc;
}

static int MPIX_Ialltoall_x(void *sendbuf, MPI_Count sendcount, MPI_Datatype sendtype,
                    void *recvbuf, MPI_Count recvcount, MPI_Datatype recvtype, MPI_Comm comm, MPI_Request *request)
{
    int rc = MPI_SUCCESS;

    if (bmpi_likely (sendcount <= BIGMPI_INT_MAX && recvcount <= BIGMPI_INT_MAX )) {
        rc = MPI_Ialltoall(sendbuf, (int)sendcount, sendtype, recvbuf, (int)recvcount, recvtype, comm, request);
    } else {
        MPI_Datatype newsendtype, newrecvtype;
        BigMPI_Type_contiguous(0,sendcount, sendtype, &newsendtype);
        BigMPI_Type_contiguous(0,recvcount, recvtype, &newrecvtype);
        MPI_Type_commit(&newsendtype);
        MPI_Type_commit(&newrecvtype);
        rc = MPI_Ialltoall(sendbuf, 1, newsendtype, recvbuf, 1, newrecvtype, comm, request);
        MPI_Type_free(&newsendtype);
        MPI_Type_free(&newrecvtype);
    }
    return rc;
}
