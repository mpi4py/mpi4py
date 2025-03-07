/* Generated with `python conf/mpiapigen.py` */

#define PyMPIAllocArray(dsttype, dst, len)                       \
  do {                                                           \
      size_t _m = (size_t) (len) * sizeof(dsttype);              \
      (dst) = (dsttype *) PyMPI_MALLOC(_m ? _m : 1);             \
  } while (0)                                                 /**/

#define PyMPIFreeArray(dst)                                      \
  do {                                                           \
    if ((dst) != NULL) PyMPI_FREE(dst);                          \
    (dst) = NULL; (void) (dst);                                  \
  } while (0)                                                 /**/

#define PyMPICastError(ERRORCODE)                                \
  do {                                                           \
    ierr = (ERRORCODE);                                          \
    (void) MPI_Comm_call_errhandler(MPI_COMM_SELF, ierr);        \
    goto fn_exit;                                                \
  } while (0)                                                 /**/

#define PyMPICastValue(dsttype, dst, srctype, src)               \
  do {                                                           \
    (dst) = (dsttype) (src);                                     \
    if ((srctype) (dst) != (src))                                \
      PyMPICastError(MPI_ERR_ARG);                               \
  } while (0)                                                 /**/

#define PyMPICastArray(dsttype, dst, srctype, src, len)          \
  do {                                                           \
    (dst) = NULL;                                                \
    if ((src) != NULL) {                                         \
      MPI_Aint _n = (MPI_Aint) (len), _i;                        \
      PyMPIAllocArray(dsttype, dst, len);                        \
      if ((dst) == NULL)                                         \
        PyMPICastError(MPI_ERR_OTHER);                           \
      for (_i = 0; _i < _n; _i++) {                              \
        (dst)[_i] = (dsttype) (src)[_i];                         \
        if ((srctype) (dst)[_i] != (src)[_i]) {                  \
          PyMPIFreeArray(dst);                                   \
          PyMPICastError(MPI_ERR_ARG);                           \
        }                                                        \
      }                                                          \
    }                                                            \
  } while (0)                                                 /**/

#define PyMPIMoveArray(dsttype, dst, srctype, src, len)          \
  do {                                                           \
    if ((src) != NULL && (dst) != NULL) {                        \
      size_t _n = (size_t) (len);                                \
      unsigned char *_buf = (unsigned char *) (src);             \
      (void) PyMPI_MEMCPY(_buf, (dst), _n * sizeof(dsttype));    \
      PyMPI_FREE(dst); (dst) = (dsttype *) _buf;                 \
    }                                                            \
  } while (0)                                                 /**/

#define PyMPICommSize(comm, n)                                   \
  do {                                                           \
    int _inter = 0;                                              \
    ierr = MPI_Comm_test_inter(comm, &_inter);                   \
    if (_inter)                                                  \
      ierr = MPI_Comm_remote_size((comm), &(n));                 \
    else                                                         \
      ierr = MPI_Comm_size((comm), &(n));                        \
    if (ierr != MPI_SUCCESS) goto fn_exit;                       \
  } while (0)                                                 /**/

#define PyMPICommLocalGroupSize(comm, n)                         \
  do {                                                           \
    ierr = MPI_Comm_size((comm), &(n));                          \
    if (ierr != MPI_SUCCESS) goto fn_exit;                       \
  } while (0)                                                 /**/

#define PyMPICommNeighborCount(comm, ns, nr)                     \
  do {                                                           \
    int _topo = MPI_UNDEFINED;                                   \
    int _i, _n; (ns) = (nr) = 0;                                 \
    ierr = MPI_Topo_test((comm), &_topo);                        \
    if (ierr != MPI_SUCCESS) goto fn_exit;                       \
    if (_topo == MPI_UNDEFINED) {                                \
      ierr = MPI_Comm_size((comm), &_n);                         \
      (ns) = (nr) = _n;                                          \
    } else if (_topo == MPI_CART) {                              \
      ierr = MPI_Cartdim_get((comm), &_n);                       \
      (ns) = (nr) = 2 * _n;                                      \
    } else if (_topo == MPI_GRAPH) {                             \
      ierr = MPI_Comm_rank((comm), &_i);                         \
      ierr = MPI_Graph_neighbors_count(                          \
               (comm), _i, &_n);                                 \
      (ns) = (nr) = _n;                                          \
    } else if (_topo == MPI_DIST_GRAPH) {                        \
      ierr = MPI_Dist_graph_neighbors_count(                     \
               (comm), &(nr), &(ns), &_i);                       \
    }                                                            \
    if (ierr != MPI_SUCCESS) goto fn_exit;                       \
  } while (0)                                                 /**/

#if !defined(PyMPI_HAVE_MPI_Type_contiguous_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_contiguous_c
static int PyMPI_Type_contiguous_c(MPI_Count a1,
                                   MPI_Datatype a2,
                                   MPI_Datatype *a3)
{
  PyMPI_WEAK_CALL(MPI_Type_contiguous_c, a1, a2, a3);
  {
  int ierr;
  int b1;
  PyMPICastValue(int, b1, MPI_Count, a1);
  ierr = MPI_Type_contiguous(b1, a2, a3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Type_contiguous_c
#define MPI_Type_contiguous_c PyMPI_Type_contiguous_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_vector_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_vector_c
static int PyMPI_Type_vector_c(MPI_Count a1,
                               MPI_Count a2,
                               MPI_Count a3,
                               MPI_Datatype a4,
                               MPI_Datatype *a5)
{
  PyMPI_WEAK_CALL(MPI_Type_vector_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b1; int b2; int b3;
  PyMPICastValue(int, b1, MPI_Count, a1);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Type_vector(b1, b2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Type_vector_c
#define MPI_Type_vector_c PyMPI_Type_vector_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_indexed_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_indexed_c
static int PyMPI_Type_indexed_c(MPI_Count a1,
                                MPI_Count *a2,
                                MPI_Count *a3,
                                MPI_Datatype a4,
                                MPI_Datatype *a5)
{
  PyMPI_WEAK_CALL(MPI_Type_indexed_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b1; int *b2 = NULL; int *b3 = NULL;
  PyMPICastValue(int, b1, MPI_Count, a1);
  PyMPICastArray(int, b2, MPI_Count, a2, a1);
  PyMPICastArray(int, b3, MPI_Count, a3, a1);
  ierr = MPI_Type_indexed(b1, b2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  return ierr;
  }
}
#undef  MPI_Type_indexed_c
#define MPI_Type_indexed_c PyMPI_Type_indexed_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_create_indexed_block_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_create_indexed_block_c
static int PyMPI_Type_create_indexed_block_c(MPI_Count a1,
                                             MPI_Count a2,
                                             MPI_Count *a3,
                                             MPI_Datatype a4,
                                             MPI_Datatype *a5)
{
  PyMPI_WEAK_CALL(MPI_Type_create_indexed_block_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b1; int b2; int *b3 = NULL;
  PyMPICastValue(int, b1, MPI_Count, a1);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(int, b3, MPI_Count, a3, a1);
  ierr = MPI_Type_create_indexed_block(b1, b2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b3);
  return ierr;
  }
}
#undef  MPI_Type_create_indexed_block_c
#define MPI_Type_create_indexed_block_c PyMPI_Type_create_indexed_block_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_create_subarray_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_create_subarray_c
static int PyMPI_Type_create_subarray_c(int a1,
                                        MPI_Count *a2,
                                        MPI_Count *a3,
                                        MPI_Count *a4,
                                        int a5,
                                        MPI_Datatype a6,
                                        MPI_Datatype *a7)
{
  PyMPI_WEAK_CALL(MPI_Type_create_subarray_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int *b2 = NULL; int *b3 = NULL; int *b4 = NULL;
  PyMPICastArray(int, b2, MPI_Count, a2, a1);
  PyMPICastArray(int, b3, MPI_Count, a3, a1);
  PyMPICastArray(int, b4, MPI_Count, a4, a1);
  ierr = MPI_Type_create_subarray(a1, b2, b3, b4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  PyMPIFreeArray(b4);
  return ierr;
  }
}
#undef  MPI_Type_create_subarray_c
#define MPI_Type_create_subarray_c PyMPI_Type_create_subarray_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_create_darray_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_create_darray_c
static int PyMPI_Type_create_darray_c(int a1,
                                      int a2,
                                      int a3,
                                      MPI_Count *a4,
                                      int *a5,
                                      int *a6,
                                      int *a7,
                                      int a8,
                                      MPI_Datatype a9,
                                      MPI_Datatype *a10)
{
  PyMPI_WEAK_CALL(MPI_Type_create_darray_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr;
  int *b4 = NULL;
  PyMPICastArray(int, b4, MPI_Count, a4, a3);
  ierr = MPI_Type_create_darray(a1, a2, a3, b4, a5, a6, a7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b4);
  return ierr;
  }
}
#undef  MPI_Type_create_darray_c
#define MPI_Type_create_darray_c PyMPI_Type_create_darray_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_create_hvector_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_create_hvector_c
static int PyMPI_Type_create_hvector_c(MPI_Count a1,
                                       MPI_Count a2,
                                       MPI_Count a3,
                                       MPI_Datatype a4,
                                       MPI_Datatype *a5)
{
  PyMPI_WEAK_CALL(MPI_Type_create_hvector_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b1; int b2; MPI_Aint b3;
  PyMPICastValue(int, b1, MPI_Count, a1);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(MPI_Aint, b3, MPI_Count, a3);
  ierr = MPI_Type_create_hvector(b1, b2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Type_create_hvector_c
#define MPI_Type_create_hvector_c PyMPI_Type_create_hvector_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_create_hindexed_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_create_hindexed_c
static int PyMPI_Type_create_hindexed_c(MPI_Count a1,
                                        MPI_Count *a2,
                                        MPI_Count *a3,
                                        MPI_Datatype a4,
                                        MPI_Datatype *a5)
{
  PyMPI_WEAK_CALL(MPI_Type_create_hindexed_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b1; int *b2 = NULL; MPI_Aint *b3 = NULL;
  PyMPICastValue(int, b1, MPI_Count, a1);
  PyMPICastArray(int, b2, MPI_Count, a2, a1);
  PyMPICastArray(MPI_Aint, b3, MPI_Count, a3, a1);
  ierr = MPI_Type_create_hindexed(b1, b2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  return ierr;
  }
}
#undef  MPI_Type_create_hindexed_c
#define MPI_Type_create_hindexed_c PyMPI_Type_create_hindexed_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_create_hindexed_block_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_create_hindexed_block_c
static int PyMPI_Type_create_hindexed_block_c(MPI_Count a1,
                                              MPI_Count a2,
                                              MPI_Count *a3,
                                              MPI_Datatype a4,
                                              MPI_Datatype *a5)
{
  PyMPI_WEAK_CALL(MPI_Type_create_hindexed_block_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b1; int b2; MPI_Aint *b3 = NULL;
  PyMPICastValue(int, b1, MPI_Count, a1);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(MPI_Aint, b3, MPI_Count, a3, a1);
  ierr = MPI_Type_create_hindexed_block(b1, b2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b3);
  return ierr;
  }
}
#undef  MPI_Type_create_hindexed_block_c
#define MPI_Type_create_hindexed_block_c PyMPI_Type_create_hindexed_block_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_create_struct_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_create_struct_c
static int PyMPI_Type_create_struct_c(MPI_Count a1,
                                      MPI_Count *a2,
                                      MPI_Count *a3,
                                      MPI_Datatype *a4,
                                      MPI_Datatype *a5)
{
  PyMPI_WEAK_CALL(MPI_Type_create_struct_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b1; int *b2 = NULL; MPI_Aint *b3 = NULL;
  PyMPICastValue(int, b1, MPI_Count, a1);
  PyMPICastArray(int, b2, MPI_Count, a2, a1);
  PyMPICastArray(MPI_Aint, b3, MPI_Count, a3, a1);
  ierr = MPI_Type_create_struct(b1, b2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  return ierr;
  }
}
#undef  MPI_Type_create_struct_c
#define MPI_Type_create_struct_c PyMPI_Type_create_struct_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_create_resized_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_create_resized_c
static int PyMPI_Type_create_resized_c(MPI_Datatype a1,
                                       MPI_Count a2,
                                       MPI_Count a3,
                                       MPI_Datatype *a4)
{
  PyMPI_WEAK_CALL(MPI_Type_create_resized_c, a1, a2, a3, a4);
  {
  int ierr;
  MPI_Aint b2; MPI_Aint b3;
  PyMPICastValue(MPI_Aint, b2, MPI_Count, a2);
  PyMPICastValue(MPI_Aint, b3, MPI_Count, a3);
  ierr = MPI_Type_create_resized(a1, b2, b3, a4);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Type_create_resized_c
#define MPI_Type_create_resized_c PyMPI_Type_create_resized_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_size_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_size_c
static int PyMPI_Type_size_c(MPI_Datatype a1,
                             MPI_Count *a2)
{
  PyMPI_WEAK_CALL(MPI_Type_size_c, a1, a2);
  {
  int ierr;
  ierr = MPI_Type_size_x(a1, a2);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Type_size_c
#define MPI_Type_size_c PyMPI_Type_size_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_get_extent_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_get_extent_c
static int PyMPI_Type_get_extent_c(MPI_Datatype a1,
                                   MPI_Count *a2,
                                   MPI_Count *a3)
{
  PyMPI_WEAK_CALL(MPI_Type_get_extent_c, a1, a2, a3);
  {
  int ierr;
  ierr = MPI_Type_get_extent_x(a1, a2, a3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Type_get_extent_c
#define MPI_Type_get_extent_c PyMPI_Type_get_extent_c
#endif

#if !defined(PyMPI_HAVE_MPI_Type_get_true_extent_c) || PyMPI_LEGACY_ABI
#undef MPI_Type_get_true_extent_c
static int PyMPI_Type_get_true_extent_c(MPI_Datatype a1,
                                        MPI_Count *a2,
                                        MPI_Count *a3)
{
  PyMPI_WEAK_CALL(MPI_Type_get_true_extent_c, a1, a2, a3);
  {
  int ierr;
  ierr = MPI_Type_get_true_extent_x(a1, a2, a3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Type_get_true_extent_c
#define MPI_Type_get_true_extent_c PyMPI_Type_get_true_extent_c
#endif

#if !defined(PyMPI_HAVE_MPI_Pack_c) || PyMPI_LEGACY_ABI
#undef MPI_Pack_c
static int PyMPI_Pack_c(void *a1,
                        MPI_Count a2,
                        MPI_Datatype a3,
                        void *a4,
                        MPI_Count a5,
                        MPI_Count *a6,
                        MPI_Comm a7)
{
  PyMPI_WEAK_CALL(MPI_Pack_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2; int b5; int b6 = 0; int *p6 = a6 ? &b6 : NULL;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  PyMPICastValue(int, b6, MPI_Count, a6 ? *a6 : 0);
  ierr = MPI_Pack(a1, b2, a3, a4, b5, p6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a6) *a6 = b6;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Pack_c
#define MPI_Pack_c PyMPI_Pack_c
#endif

#if !defined(PyMPI_HAVE_MPI_Unpack_c) || PyMPI_LEGACY_ABI
#undef MPI_Unpack_c
static int PyMPI_Unpack_c(void *a1,
                          MPI_Count a2,
                          MPI_Count *a3,
                          void *a4,
                          MPI_Count a5,
                          MPI_Datatype a6,
                          MPI_Comm a7)
{
  PyMPI_WEAK_CALL(MPI_Unpack_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2; int b3 = 0; int *p3 = a3 ? &b3 : NULL; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b3, MPI_Count, a3 ? *a3 : 0);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Unpack(a1, b2, p3, a4, b5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a3) *a3 = b3;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Unpack_c
#define MPI_Unpack_c PyMPI_Unpack_c
#endif

#if !defined(PyMPI_HAVE_MPI_Pack_size_c) || PyMPI_LEGACY_ABI
#undef MPI_Pack_size_c
static int PyMPI_Pack_size_c(MPI_Count a1,
                             MPI_Datatype a2,
                             MPI_Comm a3,
                             MPI_Count *a4)
{
  PyMPI_WEAK_CALL(MPI_Pack_size_c, a1, a2, a3, a4);
  {
  int ierr;
  int b1; int b4 = 0; int *p4 = a4 ? &b4 : NULL;
  PyMPICastValue(int, b1, MPI_Count, a1);
  ierr = MPI_Pack_size(b1, a2, a3, p4);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a4) *a4 = b4;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Pack_size_c
#define MPI_Pack_size_c PyMPI_Pack_size_c
#endif

#if !defined(PyMPI_HAVE_MPI_Pack_external_c) || PyMPI_LEGACY_ABI
#undef MPI_Pack_external_c
static int PyMPI_Pack_external_c(char *a1,
                                 void *a2,
                                 MPI_Count a3,
                                 MPI_Datatype a4,
                                 void *a5,
                                 MPI_Count a6,
                                 MPI_Count *a7)
{
  PyMPI_WEAK_CALL(MPI_Pack_external_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b3; MPI_Aint b6; MPI_Aint b7 = 0; MPI_Aint *p7 = a7 ? &b7 : NULL;
  PyMPICastValue(int, b3, MPI_Count, a3);
  PyMPICastValue(MPI_Aint, b6, MPI_Count, a6);
  PyMPICastValue(MPI_Aint, b7, MPI_Count, a7 ? *a7 : 0);
  ierr = MPI_Pack_external(a1, a2, b3, a4, a5, b6, p7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a7) *a7 = b7;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Pack_external_c
#define MPI_Pack_external_c PyMPI_Pack_external_c
#endif

#if !defined(PyMPI_HAVE_MPI_Unpack_external_c) || PyMPI_LEGACY_ABI
#undef MPI_Unpack_external_c
static int PyMPI_Unpack_external_c(char *a1,
                                   void *a2,
                                   MPI_Count a3,
                                   MPI_Count *a4,
                                   void *a5,
                                   MPI_Count a6,
                                   MPI_Datatype a7)
{
  PyMPI_WEAK_CALL(MPI_Unpack_external_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  MPI_Aint b3; MPI_Aint b4 = 0; MPI_Aint *p4 = a4 ? &b4 : NULL; int b6;
  PyMPICastValue(MPI_Aint, b3, MPI_Count, a3);
  PyMPICastValue(MPI_Aint, b4, MPI_Count, a4 ? *a4 : 0);
  PyMPICastValue(int, b6, MPI_Count, a6);
  ierr = MPI_Unpack_external(a1, a2, b3, p4, a5, b6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a4) *a4 = b4;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Unpack_external_c
#define MPI_Unpack_external_c PyMPI_Unpack_external_c
#endif

#if !defined(PyMPI_HAVE_MPI_Pack_external_size_c) || PyMPI_LEGACY_ABI
#undef MPI_Pack_external_size_c
static int PyMPI_Pack_external_size_c(char *a1,
                                      MPI_Count a2,
                                      MPI_Datatype a3,
                                      MPI_Count *a4)
{
  PyMPI_WEAK_CALL(MPI_Pack_external_size_c, a1, a2, a3, a4);
  {
  int ierr;
  int b2; MPI_Aint b4 = 0; MPI_Aint *p4 = a4 ? &b4 : NULL;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Pack_external_size(a1, b2, a3, p4);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a4) *a4 = b4;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Pack_external_size_c
#define MPI_Pack_external_size_c PyMPI_Pack_external_size_c
#endif

#if !defined(PyMPI_HAVE_MPI_Get_count_c) || PyMPI_LEGACY_ABI
#undef MPI_Get_count_c
static int PyMPI_Get_count_c(MPI_Status *a1,
                             MPI_Datatype a2,
                             MPI_Count *a3)
{
  PyMPI_WEAK_CALL(MPI_Get_count_c, a1, a2, a3);
  {
  int ierr;
  int b3 = 0; int *p3 = a3 ? &b3 : NULL;
  ierr = MPI_Get_count(a1, a2, p3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a3) *a3 = b3;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Get_count_c
#define MPI_Get_count_c PyMPI_Get_count_c
#endif

#if !defined(PyMPI_HAVE_MPI_Get_elements_c) || PyMPI_LEGACY_ABI
#undef MPI_Get_elements_c
static int PyMPI_Get_elements_c(MPI_Status *a1,
                                MPI_Datatype a2,
                                MPI_Count *a3)
{
  PyMPI_WEAK_CALL(MPI_Get_elements_c, a1, a2, a3);
  {
  int ierr;
  ierr = MPI_Get_elements_x(a1, a2, a3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Get_elements_c
#define MPI_Get_elements_c PyMPI_Get_elements_c
#endif

#if !defined(PyMPI_HAVE_MPI_Status_set_elements_c) || PyMPI_LEGACY_ABI
#undef MPI_Status_set_elements_c
static int PyMPI_Status_set_elements_c(MPI_Status *a1,
                                       MPI_Datatype a2,
                                       MPI_Count a3)
{
  PyMPI_WEAK_CALL(MPI_Status_set_elements_c, a1, a2, a3);
  {
  int ierr;
  ierr = MPI_Status_set_elements_x(a1, a2, a3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Status_set_elements_c
#define MPI_Status_set_elements_c PyMPI_Status_set_elements_c
#endif

#if !defined(PyMPI_HAVE_MPI_Buffer_attach_c) || PyMPI_LEGACY_ABI
#undef MPI_Buffer_attach_c
static int PyMPI_Buffer_attach_c(void *a1,
                                 MPI_Count a2)
{
  PyMPI_WEAK_CALL(MPI_Buffer_attach_c, a1, a2);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Buffer_attach(a1, b2);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Buffer_attach_c
#define MPI_Buffer_attach_c PyMPI_Buffer_attach_c
#endif

#if !defined(PyMPI_HAVE_MPI_Buffer_detach_c) || PyMPI_LEGACY_ABI
#undef MPI_Buffer_detach_c
static int PyMPI_Buffer_detach_c(void *a1,
                                 MPI_Count *a2)
{
  PyMPI_WEAK_CALL(MPI_Buffer_detach_c, a1, a2);
  {
  int ierr;
  int b2 = 0; int *p2 = a2 ? &b2 : NULL;
  ierr = MPI_Buffer_detach(a1, p2);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a2) *a2 = b2;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Buffer_detach_c
#define MPI_Buffer_detach_c PyMPI_Buffer_detach_c
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_attach_buffer_c) || PyMPI_LEGACY_ABI
#undef MPI_Comm_attach_buffer_c
static int PyMPI_Comm_attach_buffer_c(MPI_Comm a1,
                                      void *a2,
                                      MPI_Count a3)
{
  PyMPI_WEAK_CALL(MPI_Comm_attach_buffer_c, a1, a2, a3);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Comm_attach_buffer(a1, a2, b3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Comm_attach_buffer_c
#define MPI_Comm_attach_buffer_c PyMPI_Comm_attach_buffer_c
#endif

#if !defined(PyMPI_HAVE_MPI_Comm_detach_buffer_c) || PyMPI_LEGACY_ABI
#undef MPI_Comm_detach_buffer_c
static int PyMPI_Comm_detach_buffer_c(MPI_Comm a1,
                                      void *a2,
                                      MPI_Count *a3)
{
  PyMPI_WEAK_CALL(MPI_Comm_detach_buffer_c, a1, a2, a3);
  {
  int ierr;
  int b3 = 0; int *p3 = a3 ? &b3 : NULL;
  ierr = MPI_Comm_detach_buffer(a1, a2, p3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a3) *a3 = b3;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Comm_detach_buffer_c
#define MPI_Comm_detach_buffer_c PyMPI_Comm_detach_buffer_c
#endif

#if !defined(PyMPI_HAVE_MPI_Session_attach_buffer_c) || PyMPI_LEGACY_ABI
#undef MPI_Session_attach_buffer_c
static int PyMPI_Session_attach_buffer_c(MPI_Session a1,
                                         void *a2,
                                         MPI_Count a3)
{
  PyMPI_WEAK_CALL(MPI_Session_attach_buffer_c, a1, a2, a3);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Session_attach_buffer(a1, a2, b3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Session_attach_buffer_c
#define MPI_Session_attach_buffer_c PyMPI_Session_attach_buffer_c
#endif

#if !defined(PyMPI_HAVE_MPI_Session_detach_buffer_c) || PyMPI_LEGACY_ABI
#undef MPI_Session_detach_buffer_c
static int PyMPI_Session_detach_buffer_c(MPI_Session a1,
                                         void *a2,
                                         MPI_Count *a3)
{
  PyMPI_WEAK_CALL(MPI_Session_detach_buffer_c, a1, a2, a3);
  {
  int ierr;
  int b3 = 0; int *p3 = a3 ? &b3 : NULL;
  ierr = MPI_Session_detach_buffer(a1, a2, p3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a3) *a3 = b3;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Session_detach_buffer_c
#define MPI_Session_detach_buffer_c PyMPI_Session_detach_buffer_c
#endif

#if !defined(PyMPI_HAVE_MPI_Send_c) || PyMPI_LEGACY_ABI
#undef MPI_Send_c
static int PyMPI_Send_c(void *a1,
                        MPI_Count a2,
                        MPI_Datatype a3,
                        int a4,
                        int a5,
                        MPI_Comm a6)
{
  PyMPI_WEAK_CALL(MPI_Send_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Send(a1, b2, a3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Send_c
#define MPI_Send_c PyMPI_Send_c
#endif

#if !defined(PyMPI_HAVE_MPI_Recv_c) || PyMPI_LEGACY_ABI
#undef MPI_Recv_c
static int PyMPI_Recv_c(void *a1,
                        MPI_Count a2,
                        MPI_Datatype a3,
                        int a4,
                        int a5,
                        MPI_Comm a6,
                        MPI_Status *a7)
{
  PyMPI_WEAK_CALL(MPI_Recv_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Recv(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Recv_c
#define MPI_Recv_c PyMPI_Recv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Sendrecv_c) || PyMPI_LEGACY_ABI
#undef MPI_Sendrecv_c
static int PyMPI_Sendrecv_c(void *a1,
                            MPI_Count a2,
                            MPI_Datatype a3,
                            int a4,
                            int a5,
                            void *a6,
                            MPI_Count a7,
                            MPI_Datatype a8,
                            int a9,
                            int a10,
                            MPI_Comm a11,
                            MPI_Status *a12)
{
  PyMPI_WEAK_CALL(MPI_Sendrecv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12);
  {
  int ierr;
  int b2; int b7;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b7, MPI_Count, a7);
  ierr = MPI_Sendrecv(a1, b2, a3, a4, a5, a6, b7, a8, a9, a10, a11, a12);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Sendrecv_c
#define MPI_Sendrecv_c PyMPI_Sendrecv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Sendrecv_replace_c) || PyMPI_LEGACY_ABI
#undef MPI_Sendrecv_replace_c
static int PyMPI_Sendrecv_replace_c(void *a1,
                                    MPI_Count a2,
                                    MPI_Datatype a3,
                                    int a4,
                                    int a5,
                                    int a6,
                                    int a7,
                                    MPI_Comm a8,
                                    MPI_Status *a9)
{
  PyMPI_WEAK_CALL(MPI_Sendrecv_replace_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Sendrecv_replace(a1, b2, a3, a4, a5, a6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Sendrecv_replace_c
#define MPI_Sendrecv_replace_c PyMPI_Sendrecv_replace_c
#endif

#if !defined(PyMPI_HAVE_MPI_Bsend_c) || PyMPI_LEGACY_ABI
#undef MPI_Bsend_c
static int PyMPI_Bsend_c(void *a1,
                         MPI_Count a2,
                         MPI_Datatype a3,
                         int a4,
                         int a5,
                         MPI_Comm a6)
{
  PyMPI_WEAK_CALL(MPI_Bsend_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Bsend(a1, b2, a3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Bsend_c
#define MPI_Bsend_c PyMPI_Bsend_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ssend_c) || PyMPI_LEGACY_ABI
#undef MPI_Ssend_c
static int PyMPI_Ssend_c(void *a1,
                         MPI_Count a2,
                         MPI_Datatype a3,
                         int a4,
                         int a5,
                         MPI_Comm a6)
{
  PyMPI_WEAK_CALL(MPI_Ssend_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Ssend(a1, b2, a3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ssend_c
#define MPI_Ssend_c PyMPI_Ssend_c
#endif

#if !defined(PyMPI_HAVE_MPI_Rsend_c) || PyMPI_LEGACY_ABI
#undef MPI_Rsend_c
static int PyMPI_Rsend_c(void *a1,
                         MPI_Count a2,
                         MPI_Datatype a3,
                         int a4,
                         int a5,
                         MPI_Comm a6)
{
  PyMPI_WEAK_CALL(MPI_Rsend_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Rsend(a1, b2, a3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Rsend_c
#define MPI_Rsend_c PyMPI_Rsend_c
#endif

#if !defined(PyMPI_HAVE_MPI_Isend_c) || PyMPI_LEGACY_ABI
#undef MPI_Isend_c
static int PyMPI_Isend_c(void *a1,
                         MPI_Count a2,
                         MPI_Datatype a3,
                         int a4,
                         int a5,
                         MPI_Comm a6,
                         MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Isend_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Isend(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Isend_c
#define MPI_Isend_c PyMPI_Isend_c
#endif

#if !defined(PyMPI_HAVE_MPI_Irecv_c) || PyMPI_LEGACY_ABI
#undef MPI_Irecv_c
static int PyMPI_Irecv_c(void *a1,
                         MPI_Count a2,
                         MPI_Datatype a3,
                         int a4,
                         int a5,
                         MPI_Comm a6,
                         MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Irecv_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Irecv(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Irecv_c
#define MPI_Irecv_c PyMPI_Irecv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Isendrecv_c) || PyMPI_LEGACY_ABI
#undef MPI_Isendrecv_c
static int PyMPI_Isendrecv_c(void *a1,
                             MPI_Count a2,
                             MPI_Datatype a3,
                             int a4,
                             int a5,
                             void *a6,
                             MPI_Count a7,
                             MPI_Datatype a8,
                             int a9,
                             int a10,
                             MPI_Comm a11,
                             MPI_Request *a12)
{
  PyMPI_WEAK_CALL(MPI_Isendrecv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12);
  {
  int ierr;
  int b2; int b7;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b7, MPI_Count, a7);
  ierr = MPI_Isendrecv(a1, b2, a3, a4, a5, a6, b7, a8, a9, a10, a11, a12);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Isendrecv_c
#define MPI_Isendrecv_c PyMPI_Isendrecv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Isendrecv_replace_c) || PyMPI_LEGACY_ABI
#undef MPI_Isendrecv_replace_c
static int PyMPI_Isendrecv_replace_c(void *a1,
                                     MPI_Count a2,
                                     MPI_Datatype a3,
                                     int a4,
                                     int a5,
                                     int a6,
                                     int a7,
                                     MPI_Comm a8,
                                     MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Isendrecv_replace_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Isendrecv_replace(a1, b2, a3, a4, a5, a6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Isendrecv_replace_c
#define MPI_Isendrecv_replace_c PyMPI_Isendrecv_replace_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ibsend_c) || PyMPI_LEGACY_ABI
#undef MPI_Ibsend_c
static int PyMPI_Ibsend_c(void *a1,
                          MPI_Count a2,
                          MPI_Datatype a3,
                          int a4,
                          int a5,
                          MPI_Comm a6,
                          MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Ibsend_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Ibsend(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ibsend_c
#define MPI_Ibsend_c PyMPI_Ibsend_c
#endif

#if !defined(PyMPI_HAVE_MPI_Issend_c) || PyMPI_LEGACY_ABI
#undef MPI_Issend_c
static int PyMPI_Issend_c(void *a1,
                          MPI_Count a2,
                          MPI_Datatype a3,
                          int a4,
                          int a5,
                          MPI_Comm a6,
                          MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Issend_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Issend(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Issend_c
#define MPI_Issend_c PyMPI_Issend_c
#endif

#if !defined(PyMPI_HAVE_MPI_Irsend_c) || PyMPI_LEGACY_ABI
#undef MPI_Irsend_c
static int PyMPI_Irsend_c(void *a1,
                          MPI_Count a2,
                          MPI_Datatype a3,
                          int a4,
                          int a5,
                          MPI_Comm a6,
                          MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Irsend_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Irsend(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Irsend_c
#define MPI_Irsend_c PyMPI_Irsend_c
#endif

#if !defined(PyMPI_HAVE_MPI_Send_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Send_init_c
static int PyMPI_Send_init_c(void *a1,
                             MPI_Count a2,
                             MPI_Datatype a3,
                             int a4,
                             int a5,
                             MPI_Comm a6,
                             MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Send_init_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Send_init(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Send_init_c
#define MPI_Send_init_c PyMPI_Send_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Recv_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Recv_init_c
static int PyMPI_Recv_init_c(void *a1,
                             MPI_Count a2,
                             MPI_Datatype a3,
                             int a4,
                             int a5,
                             MPI_Comm a6,
                             MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Recv_init_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Recv_init(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Recv_init_c
#define MPI_Recv_init_c PyMPI_Recv_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Bsend_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Bsend_init_c
static int PyMPI_Bsend_init_c(void *a1,
                              MPI_Count a2,
                              MPI_Datatype a3,
                              int a4,
                              int a5,
                              MPI_Comm a6,
                              MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Bsend_init_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Bsend_init(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Bsend_init_c
#define MPI_Bsend_init_c PyMPI_Bsend_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ssend_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Ssend_init_c
static int PyMPI_Ssend_init_c(void *a1,
                              MPI_Count a2,
                              MPI_Datatype a3,
                              int a4,
                              int a5,
                              MPI_Comm a6,
                              MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Ssend_init_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Ssend_init(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ssend_init_c
#define MPI_Ssend_init_c PyMPI_Ssend_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Rsend_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Rsend_init_c
static int PyMPI_Rsend_init_c(void *a1,
                              MPI_Count a2,
                              MPI_Datatype a3,
                              int a4,
                              int a5,
                              MPI_Comm a6,
                              MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Rsend_init_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Rsend_init(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Rsend_init_c
#define MPI_Rsend_init_c PyMPI_Rsend_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Mrecv_c) || PyMPI_LEGACY_ABI
#undef MPI_Mrecv_c
static int PyMPI_Mrecv_c(void *a1,
                         MPI_Count a2,
                         MPI_Datatype a3,
                         MPI_Message *a4,
                         MPI_Status *a5)
{
  PyMPI_WEAK_CALL(MPI_Mrecv_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Mrecv(a1, b2, a3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Mrecv_c
#define MPI_Mrecv_c PyMPI_Mrecv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Imrecv_c) || PyMPI_LEGACY_ABI
#undef MPI_Imrecv_c
static int PyMPI_Imrecv_c(void *a1,
                          MPI_Count a2,
                          MPI_Datatype a3,
                          MPI_Message *a4,
                          MPI_Request *a5)
{
  PyMPI_WEAK_CALL(MPI_Imrecv_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Imrecv(a1, b2, a3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Imrecv_c
#define MPI_Imrecv_c PyMPI_Imrecv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Bcast_c) || PyMPI_LEGACY_ABI
#undef MPI_Bcast_c
static int PyMPI_Bcast_c(void *a1,
                         MPI_Count a2,
                         MPI_Datatype a3,
                         int a4,
                         MPI_Comm a5)
{
  PyMPI_WEAK_CALL(MPI_Bcast_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Bcast(a1, b2, a3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Bcast_c
#define MPI_Bcast_c PyMPI_Bcast_c
#endif

#if !defined(PyMPI_HAVE_MPI_Gather_c) || PyMPI_LEGACY_ABI
#undef MPI_Gather_c
static int PyMPI_Gather_c(void *a1,
                          MPI_Count a2,
                          MPI_Datatype a3,
                          void *a4,
                          MPI_Count a5,
                          MPI_Datatype a6,
                          int a7,
                          MPI_Comm a8)
{
  PyMPI_WEAK_CALL(MPI_Gather_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Gather(a1, b2, a3, a4, b5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Gather_c
#define MPI_Gather_c PyMPI_Gather_c
#endif

#if !defined(PyMPI_HAVE_MPI_Gatherv_c) || PyMPI_LEGACY_ABI
#undef MPI_Gatherv_c
static int PyMPI_Gatherv_c(void *a1,
                           MPI_Count a2,
                           MPI_Datatype a3,
                           void *a4,
                           MPI_Count *a5,
                           MPI_Aint *a6,
                           MPI_Datatype a7,
                           int a8,
                           MPI_Comm a9)
{
  PyMPI_WEAK_CALL(MPI_Gatherv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr; int n;
  int b2; int *b5 = NULL; int *b6 = NULL;
  PyMPICommSize(a9, n);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(int, b5, MPI_Count, a5, n);
  PyMPICastArray(int, b6, MPI_Aint, a6, n);
  ierr = MPI_Gatherv(a1, b2, a3, a4, b5, b6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b5);
  PyMPIFreeArray(b6);
  return ierr;
  }
}
#undef  MPI_Gatherv_c
#define MPI_Gatherv_c PyMPI_Gatherv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Scatter_c) || PyMPI_LEGACY_ABI
#undef MPI_Scatter_c
static int PyMPI_Scatter_c(void *a1,
                           MPI_Count a2,
                           MPI_Datatype a3,
                           void *a4,
                           MPI_Count a5,
                           MPI_Datatype a6,
                           int a7,
                           MPI_Comm a8)
{
  PyMPI_WEAK_CALL(MPI_Scatter_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Scatter(a1, b2, a3, a4, b5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Scatter_c
#define MPI_Scatter_c PyMPI_Scatter_c
#endif

#if !defined(PyMPI_HAVE_MPI_Scatterv_c) || PyMPI_LEGACY_ABI
#undef MPI_Scatterv_c
static int PyMPI_Scatterv_c(void *a1,
                            MPI_Count *a2,
                            MPI_Aint *a3,
                            MPI_Datatype a4,
                            void *a5,
                            MPI_Count a6,
                            MPI_Datatype a7,
                            int a8,
                            MPI_Comm a9)
{
  PyMPI_WEAK_CALL(MPI_Scatterv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr; int n;
  int *b2 = NULL; int *b3 = NULL; int b6;
  PyMPICommSize(a9, n);
  PyMPICastArray(int, b2, MPI_Count, a2, n);
  PyMPICastArray(int, b3, MPI_Aint, a3, n);
  PyMPICastValue(int, b6, MPI_Count, a6);
  ierr = MPI_Scatterv(a1, b2, b3, a4, a5, b6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  return ierr;
  }
}
#undef  MPI_Scatterv_c
#define MPI_Scatterv_c PyMPI_Scatterv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Allgather_c) || PyMPI_LEGACY_ABI
#undef MPI_Allgather_c
static int PyMPI_Allgather_c(void *a1,
                             MPI_Count a2,
                             MPI_Datatype a3,
                             void *a4,
                             MPI_Count a5,
                             MPI_Datatype a6,
                             MPI_Comm a7)
{
  PyMPI_WEAK_CALL(MPI_Allgather_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Allgather(a1, b2, a3, a4, b5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Allgather_c
#define MPI_Allgather_c PyMPI_Allgather_c
#endif

#if !defined(PyMPI_HAVE_MPI_Allgatherv_c) || PyMPI_LEGACY_ABI
#undef MPI_Allgatherv_c
static int PyMPI_Allgatherv_c(void *a1,
                              MPI_Count a2,
                              MPI_Datatype a3,
                              void *a4,
                              MPI_Count *a5,
                              MPI_Aint *a6,
                              MPI_Datatype a7,
                              MPI_Comm a8)
{
  PyMPI_WEAK_CALL(MPI_Allgatherv_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr; int n;
  int b2; int *b5 = NULL; int *b6 = NULL;
  PyMPICommSize(a8, n);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(int, b5, MPI_Count, a5, n);
  PyMPICastArray(int, b6, MPI_Aint, a6, n);
  ierr = MPI_Allgatherv(a1, b2, a3, a4, b5, b6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b5);
  PyMPIFreeArray(b6);
  return ierr;
  }
}
#undef  MPI_Allgatherv_c
#define MPI_Allgatherv_c PyMPI_Allgatherv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Alltoall_c) || PyMPI_LEGACY_ABI
#undef MPI_Alltoall_c
static int PyMPI_Alltoall_c(void *a1,
                            MPI_Count a2,
                            MPI_Datatype a3,
                            void *a4,
                            MPI_Count a5,
                            MPI_Datatype a6,
                            MPI_Comm a7)
{
  PyMPI_WEAK_CALL(MPI_Alltoall_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Alltoall(a1, b2, a3, a4, b5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Alltoall_c
#define MPI_Alltoall_c PyMPI_Alltoall_c
#endif

#if !defined(PyMPI_HAVE_MPI_Alltoallv_c) || PyMPI_LEGACY_ABI
#undef MPI_Alltoallv_c
static int PyMPI_Alltoallv_c(void *a1,
                             MPI_Count *a2,
                             MPI_Aint *a3,
                             MPI_Datatype a4,
                             void *a5,
                             MPI_Count *a6,
                             MPI_Aint *a7,
                             MPI_Datatype a8,
                             MPI_Comm a9)
{
  PyMPI_WEAK_CALL(MPI_Alltoallv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr; int n;
  int *b2 = NULL; int *b3 = NULL; int *b6 = NULL; int *b7 = NULL;
  PyMPICommSize(a9, n);
  PyMPICastArray(int, b2, MPI_Count, a2, n);
  PyMPICastArray(int, b3, MPI_Aint, a3, n);
  PyMPICastArray(int, b6, MPI_Count, a6, n);
  PyMPICastArray(int, b7, MPI_Aint, a7, n);
  ierr = MPI_Alltoallv(a1, b2, b3, a4, a5, b6, b7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  PyMPIFreeArray(b6);
  PyMPIFreeArray(b7);
  return ierr;
  }
}
#undef  MPI_Alltoallv_c
#define MPI_Alltoallv_c PyMPI_Alltoallv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Alltoallw_c) || PyMPI_LEGACY_ABI
#undef MPI_Alltoallw_c
static int PyMPI_Alltoallw_c(void *a1,
                             MPI_Count *a2,
                             MPI_Aint *a3,
                             MPI_Datatype *a4,
                             void *a5,
                             MPI_Count *a6,
                             MPI_Aint *a7,
                             MPI_Datatype *a8,
                             MPI_Comm a9)
{
  PyMPI_WEAK_CALL(MPI_Alltoallw_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr; int n;
  int *b2 = NULL; int *b3 = NULL; int *b6 = NULL; int *b7 = NULL;
  PyMPICommSize(a9, n);
  PyMPICastArray(int, b2, MPI_Count, a2, n);
  PyMPICastArray(int, b3, MPI_Aint, a3, n);
  PyMPICastArray(int, b6, MPI_Count, a6, n);
  PyMPICastArray(int, b7, MPI_Aint, a7, n);
  ierr = MPI_Alltoallw(a1, b2, b3, a4, a5, b6, b7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  PyMPIFreeArray(b6);
  PyMPIFreeArray(b7);
  return ierr;
  }
}
#undef  MPI_Alltoallw_c
#define MPI_Alltoallw_c PyMPI_Alltoallw_c
#endif

#if !defined(PyMPI_HAVE_MPI_Reduce_local_c) || PyMPI_LEGACY_ABI
#undef MPI_Reduce_local_c
static int PyMPI_Reduce_local_c(void *a1,
                                void *a2,
                                MPI_Count a3,
                                MPI_Datatype a4,
                                MPI_Op a5)
{
  PyMPI_WEAK_CALL(MPI_Reduce_local_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Reduce_local(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Reduce_local_c
#define MPI_Reduce_local_c PyMPI_Reduce_local_c
#endif

#if !defined(PyMPI_HAVE_MPI_Reduce_c) || PyMPI_LEGACY_ABI
#undef MPI_Reduce_c
static int PyMPI_Reduce_c(void *a1,
                          void *a2,
                          MPI_Count a3,
                          MPI_Datatype a4,
                          MPI_Op a5,
                          int a6,
                          MPI_Comm a7)
{
  PyMPI_WEAK_CALL(MPI_Reduce_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Reduce(a1, a2, b3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Reduce_c
#define MPI_Reduce_c PyMPI_Reduce_c
#endif

#if !defined(PyMPI_HAVE_MPI_Allreduce_c) || PyMPI_LEGACY_ABI
#undef MPI_Allreduce_c
static int PyMPI_Allreduce_c(void *a1,
                             void *a2,
                             MPI_Count a3,
                             MPI_Datatype a4,
                             MPI_Op a5,
                             MPI_Comm a6)
{
  PyMPI_WEAK_CALL(MPI_Allreduce_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Allreduce(a1, a2, b3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Allreduce_c
#define MPI_Allreduce_c PyMPI_Allreduce_c
#endif

#if !defined(PyMPI_HAVE_MPI_Reduce_scatter_block_c) || PyMPI_LEGACY_ABI
#undef MPI_Reduce_scatter_block_c
static int PyMPI_Reduce_scatter_block_c(void *a1,
                                        void *a2,
                                        MPI_Count a3,
                                        MPI_Datatype a4,
                                        MPI_Op a5,
                                        MPI_Comm a6)
{
  PyMPI_WEAK_CALL(MPI_Reduce_scatter_block_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Reduce_scatter_block(a1, a2, b3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Reduce_scatter_block_c
#define MPI_Reduce_scatter_block_c PyMPI_Reduce_scatter_block_c
#endif

#if !defined(PyMPI_HAVE_MPI_Reduce_scatter_c) || PyMPI_LEGACY_ABI
#undef MPI_Reduce_scatter_c
static int PyMPI_Reduce_scatter_c(void *a1,
                                  void *a2,
                                  MPI_Count *a3,
                                  MPI_Datatype a4,
                                  MPI_Op a5,
                                  MPI_Comm a6)
{
  PyMPI_WEAK_CALL(MPI_Reduce_scatter_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr; int n;
  int *b3 = NULL;
  PyMPICommLocalGroupSize(a6, n);
  PyMPICastArray(int, b3, MPI_Count, a3, n);
  ierr = MPI_Reduce_scatter(a1, a2, b3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b3);
  return ierr;
  }
}
#undef  MPI_Reduce_scatter_c
#define MPI_Reduce_scatter_c PyMPI_Reduce_scatter_c
#endif

#if !defined(PyMPI_HAVE_MPI_Scan_c) || PyMPI_LEGACY_ABI
#undef MPI_Scan_c
static int PyMPI_Scan_c(void *a1,
                        void *a2,
                        MPI_Count a3,
                        MPI_Datatype a4,
                        MPI_Op a5,
                        MPI_Comm a6)
{
  PyMPI_WEAK_CALL(MPI_Scan_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Scan(a1, a2, b3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Scan_c
#define MPI_Scan_c PyMPI_Scan_c
#endif

#if !defined(PyMPI_HAVE_MPI_Exscan_c) || PyMPI_LEGACY_ABI
#undef MPI_Exscan_c
static int PyMPI_Exscan_c(void *a1,
                          void *a2,
                          MPI_Count a3,
                          MPI_Datatype a4,
                          MPI_Op a5,
                          MPI_Comm a6)
{
  PyMPI_WEAK_CALL(MPI_Exscan_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Exscan(a1, a2, b3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Exscan_c
#define MPI_Exscan_c PyMPI_Exscan_c
#endif

#if !defined(PyMPI_HAVE_MPI_Neighbor_allgather_c) || PyMPI_LEGACY_ABI
#undef MPI_Neighbor_allgather_c
static int PyMPI_Neighbor_allgather_c(void *a1,
                                      MPI_Count a2,
                                      MPI_Datatype a3,
                                      void *a4,
                                      MPI_Count a5,
                                      MPI_Datatype a6,
                                      MPI_Comm a7)
{
  PyMPI_WEAK_CALL(MPI_Neighbor_allgather_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Neighbor_allgather(a1, b2, a3, a4, b5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Neighbor_allgather_c
#define MPI_Neighbor_allgather_c PyMPI_Neighbor_allgather_c
#endif

#if !defined(PyMPI_HAVE_MPI_Neighbor_allgatherv_c) || PyMPI_LEGACY_ABI
#undef MPI_Neighbor_allgatherv_c
static int PyMPI_Neighbor_allgatherv_c(void *a1,
                                       MPI_Count a2,
                                       MPI_Datatype a3,
                                       void *a4,
                                       MPI_Count *a5,
                                       MPI_Aint *a6,
                                       MPI_Datatype a7,
                                       MPI_Comm a8)
{
  PyMPI_WEAK_CALL(MPI_Neighbor_allgatherv_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr; int ns, nr;
  int b2; int *b5 = NULL; int *b6 = NULL;
  PyMPICommNeighborCount(a8, ns, nr);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(int, b5, MPI_Count, a5, nr);
  PyMPICastArray(int, b6, MPI_Aint, a6, nr);
  ierr = MPI_Neighbor_allgatherv(a1, b2, a3, a4, b5, b6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b5);
  PyMPIFreeArray(b6);
  return ierr;
  }
}
#undef  MPI_Neighbor_allgatherv_c
#define MPI_Neighbor_allgatherv_c PyMPI_Neighbor_allgatherv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Neighbor_alltoall_c) || PyMPI_LEGACY_ABI
#undef MPI_Neighbor_alltoall_c
static int PyMPI_Neighbor_alltoall_c(void *a1,
                                     MPI_Count a2,
                                     MPI_Datatype a3,
                                     void *a4,
                                     MPI_Count a5,
                                     MPI_Datatype a6,
                                     MPI_Comm a7)
{
  PyMPI_WEAK_CALL(MPI_Neighbor_alltoall_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Neighbor_alltoall(a1, b2, a3, a4, b5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Neighbor_alltoall_c
#define MPI_Neighbor_alltoall_c PyMPI_Neighbor_alltoall_c
#endif

#if !defined(PyMPI_HAVE_MPI_Neighbor_alltoallv_c) || PyMPI_LEGACY_ABI
#undef MPI_Neighbor_alltoallv_c
static int PyMPI_Neighbor_alltoallv_c(void *a1,
                                      MPI_Count *a2,
                                      MPI_Aint *a3,
                                      MPI_Datatype a4,
                                      void *a5,
                                      MPI_Count *a6,
                                      MPI_Aint *a7,
                                      MPI_Datatype a8,
                                      MPI_Comm a9)
{
  PyMPI_WEAK_CALL(MPI_Neighbor_alltoallv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr; int ns, nr;
  int *b2 = NULL; int *b3 = NULL; int *b6 = NULL; int *b7 = NULL;
  PyMPICommNeighborCount(a9, ns, nr);
  PyMPICastArray(int, b2, MPI_Count, a2, ns);
  PyMPICastArray(int, b3, MPI_Aint, a3, ns);
  PyMPICastArray(int, b6, MPI_Count, a6, nr);
  PyMPICastArray(int, b7, MPI_Aint, a7, nr);
  ierr = MPI_Neighbor_alltoallv(a1, b2, b3, a4, a5, b6, b7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  PyMPIFreeArray(b6);
  PyMPIFreeArray(b7);
  return ierr;
  }
}
#undef  MPI_Neighbor_alltoallv_c
#define MPI_Neighbor_alltoallv_c PyMPI_Neighbor_alltoallv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Neighbor_alltoallw_c) || PyMPI_LEGACY_ABI
#undef MPI_Neighbor_alltoallw_c
static int PyMPI_Neighbor_alltoallw_c(void *a1,
                                      MPI_Count *a2,
                                      MPI_Aint *a3,
                                      MPI_Datatype *a4,
                                      void *a5,
                                      MPI_Count *a6,
                                      MPI_Aint *a7,
                                      MPI_Datatype *a8,
                                      MPI_Comm a9)
{
  PyMPI_WEAK_CALL(MPI_Neighbor_alltoallw_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr; int ns, nr;
  int *b2 = NULL; int *b6 = NULL;
  PyMPICommNeighborCount(a9, ns, nr);
  PyMPICastArray(int, b2, MPI_Count, a2, ns);
  PyMPICastArray(int, b6, MPI_Count, a6, nr);
  ierr = MPI_Neighbor_alltoallw(a1, b2, a3, a4, a5, b6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b6);
  return ierr;
  }
}
#undef  MPI_Neighbor_alltoallw_c
#define MPI_Neighbor_alltoallw_c PyMPI_Neighbor_alltoallw_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ibcast_c) || PyMPI_LEGACY_ABI
#undef MPI_Ibcast_c
static int PyMPI_Ibcast_c(void *a1,
                          MPI_Count a2,
                          MPI_Datatype a3,
                          int a4,
                          MPI_Comm a5,
                          MPI_Request *a6)
{
  PyMPI_WEAK_CALL(MPI_Ibcast_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Ibcast(a1, b2, a3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ibcast_c
#define MPI_Ibcast_c PyMPI_Ibcast_c
#endif

#if !defined(PyMPI_HAVE_MPI_Igather_c) || PyMPI_LEGACY_ABI
#undef MPI_Igather_c
static int PyMPI_Igather_c(void *a1,
                           MPI_Count a2,
                           MPI_Datatype a3,
                           void *a4,
                           MPI_Count a5,
                           MPI_Datatype a6,
                           int a7,
                           MPI_Comm a8,
                           MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Igather_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Igather(a1, b2, a3, a4, b5, a6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Igather_c
#define MPI_Igather_c PyMPI_Igather_c
#endif

#if !defined(PyMPI_HAVE_MPI_Igatherv_c) || PyMPI_LEGACY_ABI
#undef MPI_Igatherv_c
static int PyMPI_Igatherv_c(void *a1,
                            MPI_Count a2,
                            MPI_Datatype a3,
                            void *a4,
                            MPI_Count *a5,
                            MPI_Aint *a6,
                            MPI_Datatype a7,
                            int a8,
                            MPI_Comm a9,
                            MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Igatherv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr; int n;
  int b2; int *b5 = NULL; int *b6 = NULL;
  PyMPICommSize(a9, n);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(int, b5, MPI_Count, a5, n);
  PyMPIMoveArray(int, b5, MPI_Count, a5, n);
  PyMPICastArray(int, b6, MPI_Aint, a6, n);
  PyMPIMoveArray(int, b6, MPI_Aint, a6, n);
  ierr = MPI_Igatherv(a1, b2, a3, a4, b5, b6, a7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Igatherv_c
#define MPI_Igatherv_c PyMPI_Igatherv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Iscatter_c) || PyMPI_LEGACY_ABI
#undef MPI_Iscatter_c
static int PyMPI_Iscatter_c(void *a1,
                            MPI_Count a2,
                            MPI_Datatype a3,
                            void *a4,
                            MPI_Count a5,
                            MPI_Datatype a6,
                            int a7,
                            MPI_Comm a8,
                            MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Iscatter_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Iscatter(a1, b2, a3, a4, b5, a6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Iscatter_c
#define MPI_Iscatter_c PyMPI_Iscatter_c
#endif

#if !defined(PyMPI_HAVE_MPI_Iscatterv_c) || PyMPI_LEGACY_ABI
#undef MPI_Iscatterv_c
static int PyMPI_Iscatterv_c(void *a1,
                             MPI_Count *a2,
                             MPI_Aint *a3,
                             MPI_Datatype a4,
                             void *a5,
                             MPI_Count a6,
                             MPI_Datatype a7,
                             int a8,
                             MPI_Comm a9,
                             MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Iscatterv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr; int n;
  int *b2 = NULL; int *b3 = NULL; int b6;
  PyMPICommSize(a9, n);
  PyMPICastArray(int, b2, MPI_Count, a2, n);
  PyMPIMoveArray(int, b2, MPI_Count, a2, n);
  PyMPICastArray(int, b3, MPI_Aint, a3, n);
  PyMPIMoveArray(int, b3, MPI_Aint, a3, n);
  PyMPICastValue(int, b6, MPI_Count, a6);
  ierr = MPI_Iscatterv(a1, b2, b3, a4, a5, b6, a7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Iscatterv_c
#define MPI_Iscatterv_c PyMPI_Iscatterv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Iallgather_c) || PyMPI_LEGACY_ABI
#undef MPI_Iallgather_c
static int PyMPI_Iallgather_c(void *a1,
                              MPI_Count a2,
                              MPI_Datatype a3,
                              void *a4,
                              MPI_Count a5,
                              MPI_Datatype a6,
                              MPI_Comm a7,
                              MPI_Request *a8)
{
  PyMPI_WEAK_CALL(MPI_Iallgather_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Iallgather(a1, b2, a3, a4, b5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Iallgather_c
#define MPI_Iallgather_c PyMPI_Iallgather_c
#endif

#if !defined(PyMPI_HAVE_MPI_Iallgatherv_c) || PyMPI_LEGACY_ABI
#undef MPI_Iallgatherv_c
static int PyMPI_Iallgatherv_c(void *a1,
                               MPI_Count a2,
                               MPI_Datatype a3,
                               void *a4,
                               MPI_Count *a5,
                               MPI_Aint *a6,
                               MPI_Datatype a7,
                               MPI_Comm a8,
                               MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Iallgatherv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr; int n;
  int b2; int *b5 = NULL; int *b6 = NULL;
  PyMPICommSize(a8, n);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(int, b5, MPI_Count, a5, n);
  PyMPIMoveArray(int, b5, MPI_Count, a5, n);
  PyMPICastArray(int, b6, MPI_Aint, a6, n);
  PyMPIMoveArray(int, b6, MPI_Aint, a6, n);
  ierr = MPI_Iallgatherv(a1, b2, a3, a4, b5, b6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Iallgatherv_c
#define MPI_Iallgatherv_c PyMPI_Iallgatherv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ialltoall_c) || PyMPI_LEGACY_ABI
#undef MPI_Ialltoall_c
static int PyMPI_Ialltoall_c(void *a1,
                             MPI_Count a2,
                             MPI_Datatype a3,
                             void *a4,
                             MPI_Count a5,
                             MPI_Datatype a6,
                             MPI_Comm a7,
                             MPI_Request *a8)
{
  PyMPI_WEAK_CALL(MPI_Ialltoall_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Ialltoall(a1, b2, a3, a4, b5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ialltoall_c
#define MPI_Ialltoall_c PyMPI_Ialltoall_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ialltoallv_c) || PyMPI_LEGACY_ABI
#undef MPI_Ialltoallv_c
static int PyMPI_Ialltoallv_c(void *a1,
                              MPI_Count *a2,
                              MPI_Aint *a3,
                              MPI_Datatype a4,
                              void *a5,
                              MPI_Count *a6,
                              MPI_Aint *a7,
                              MPI_Datatype a8,
                              MPI_Comm a9,
                              MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Ialltoallv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr; int n;
  int *b2 = NULL; int *b3 = NULL; int *b6 = NULL; int *b7 = NULL;
  PyMPICommSize(a9, n);
  PyMPICastArray(int, b2, MPI_Count, a2, n);
  PyMPIMoveArray(int, b2, MPI_Count, a2, n);
  PyMPICastArray(int, b3, MPI_Aint, a3, n);
  PyMPIMoveArray(int, b3, MPI_Aint, a3, n);
  PyMPICastArray(int, b6, MPI_Count, a6, n);
  PyMPIMoveArray(int, b6, MPI_Count, a6, n);
  PyMPICastArray(int, b7, MPI_Aint, a7, n);
  PyMPIMoveArray(int, b7, MPI_Aint, a7, n);
  ierr = MPI_Ialltoallv(a1, b2, b3, a4, a5, b6, b7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ialltoallv_c
#define MPI_Ialltoallv_c PyMPI_Ialltoallv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ialltoallw_c) || PyMPI_LEGACY_ABI
#undef MPI_Ialltoallw_c
static int PyMPI_Ialltoallw_c(void *a1,
                              MPI_Count *a2,
                              MPI_Aint *a3,
                              MPI_Datatype *a4,
                              void *a5,
                              MPI_Count *a6,
                              MPI_Aint *a7,
                              MPI_Datatype *a8,
                              MPI_Comm a9,
                              MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Ialltoallw_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr; int n;
  int *b2 = NULL; int *b3 = NULL; int *b6 = NULL; int *b7 = NULL;
  PyMPICommSize(a9, n);
  PyMPICastArray(int, b2, MPI_Count, a2, n);
  PyMPIMoveArray(int, b2, MPI_Count, a2, n);
  PyMPICastArray(int, b3, MPI_Aint, a3, n);
  PyMPIMoveArray(int, b3, MPI_Aint, a3, n);
  PyMPICastArray(int, b6, MPI_Count, a6, n);
  PyMPIMoveArray(int, b6, MPI_Count, a6, n);
  PyMPICastArray(int, b7, MPI_Aint, a7, n);
  PyMPIMoveArray(int, b7, MPI_Aint, a7, n);
  ierr = MPI_Ialltoallw(a1, b2, b3, a4, a5, b6, b7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ialltoallw_c
#define MPI_Ialltoallw_c PyMPI_Ialltoallw_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ireduce_c) || PyMPI_LEGACY_ABI
#undef MPI_Ireduce_c
static int PyMPI_Ireduce_c(void *a1,
                           void *a2,
                           MPI_Count a3,
                           MPI_Datatype a4,
                           MPI_Op a5,
                           int a6,
                           MPI_Comm a7,
                           MPI_Request *a8)
{
  PyMPI_WEAK_CALL(MPI_Ireduce_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Ireduce(a1, a2, b3, a4, a5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ireduce_c
#define MPI_Ireduce_c PyMPI_Ireduce_c
#endif

#if !defined(PyMPI_HAVE_MPI_Iallreduce_c) || PyMPI_LEGACY_ABI
#undef MPI_Iallreduce_c
static int PyMPI_Iallreduce_c(void *a1,
                              void *a2,
                              MPI_Count a3,
                              MPI_Datatype a4,
                              MPI_Op a5,
                              MPI_Comm a6,
                              MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Iallreduce_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Iallreduce(a1, a2, b3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Iallreduce_c
#define MPI_Iallreduce_c PyMPI_Iallreduce_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ireduce_scatter_block_c) || PyMPI_LEGACY_ABI
#undef MPI_Ireduce_scatter_block_c
static int PyMPI_Ireduce_scatter_block_c(void *a1,
                                         void *a2,
                                         MPI_Count a3,
                                         MPI_Datatype a4,
                                         MPI_Op a5,
                                         MPI_Comm a6,
                                         MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Ireduce_scatter_block_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Ireduce_scatter_block(a1, a2, b3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ireduce_scatter_block_c
#define MPI_Ireduce_scatter_block_c PyMPI_Ireduce_scatter_block_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ireduce_scatter_c) || PyMPI_LEGACY_ABI
#undef MPI_Ireduce_scatter_c
static int PyMPI_Ireduce_scatter_c(void *a1,
                                   void *a2,
                                   MPI_Count *a3,
                                   MPI_Datatype a4,
                                   MPI_Op a5,
                                   MPI_Comm a6,
                                   MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Ireduce_scatter_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr; int n;
  int *b3 = NULL;
  PyMPICommLocalGroupSize(a6, n);
  PyMPICastArray(int, b3, MPI_Count, a3, n);
  PyMPIMoveArray(int, b3, MPI_Count, a3, n);
  ierr = MPI_Ireduce_scatter(a1, a2, b3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ireduce_scatter_c
#define MPI_Ireduce_scatter_c PyMPI_Ireduce_scatter_c
#endif

#if !defined(PyMPI_HAVE_MPI_Iscan_c) || PyMPI_LEGACY_ABI
#undef MPI_Iscan_c
static int PyMPI_Iscan_c(void *a1,
                         void *a2,
                         MPI_Count a3,
                         MPI_Datatype a4,
                         MPI_Op a5,
                         MPI_Comm a6,
                         MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Iscan_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Iscan(a1, a2, b3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Iscan_c
#define MPI_Iscan_c PyMPI_Iscan_c
#endif

#if !defined(PyMPI_HAVE_MPI_Iexscan_c) || PyMPI_LEGACY_ABI
#undef MPI_Iexscan_c
static int PyMPI_Iexscan_c(void *a1,
                           void *a2,
                           MPI_Count a3,
                           MPI_Datatype a4,
                           MPI_Op a5,
                           MPI_Comm a6,
                           MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Iexscan_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Iexscan(a1, a2, b3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Iexscan_c
#define MPI_Iexscan_c PyMPI_Iexscan_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ineighbor_allgather_c) || PyMPI_LEGACY_ABI
#undef MPI_Ineighbor_allgather_c
static int PyMPI_Ineighbor_allgather_c(void *a1,
                                       MPI_Count a2,
                                       MPI_Datatype a3,
                                       void *a4,
                                       MPI_Count a5,
                                       MPI_Datatype a6,
                                       MPI_Comm a7,
                                       MPI_Request *a8)
{
  PyMPI_WEAK_CALL(MPI_Ineighbor_allgather_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Ineighbor_allgather(a1, b2, a3, a4, b5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ineighbor_allgather_c
#define MPI_Ineighbor_allgather_c PyMPI_Ineighbor_allgather_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ineighbor_allgatherv_c) || PyMPI_LEGACY_ABI
#undef MPI_Ineighbor_allgatherv_c
static int PyMPI_Ineighbor_allgatherv_c(void *a1,
                                        MPI_Count a2,
                                        MPI_Datatype a3,
                                        void *a4,
                                        MPI_Count *a5,
                                        MPI_Aint *a6,
                                        MPI_Datatype a7,
                                        MPI_Comm a8,
                                        MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Ineighbor_allgatherv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr; int ns, nr;
  int b2; int *b5 = NULL; int *b6 = NULL;
  PyMPICommNeighborCount(a8, ns, nr);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(int, b5, MPI_Count, a5, nr);
  PyMPIMoveArray(int, b5, MPI_Count, a5, nr);
  PyMPICastArray(int, b6, MPI_Aint, a6, nr);
  PyMPIMoveArray(int, b6, MPI_Aint, a6, nr);
  ierr = MPI_Ineighbor_allgatherv(a1, b2, a3, a4, b5, b6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ineighbor_allgatherv_c
#define MPI_Ineighbor_allgatherv_c PyMPI_Ineighbor_allgatherv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ineighbor_alltoall_c) || PyMPI_LEGACY_ABI
#undef MPI_Ineighbor_alltoall_c
static int PyMPI_Ineighbor_alltoall_c(void *a1,
                                      MPI_Count a2,
                                      MPI_Datatype a3,
                                      void *a4,
                                      MPI_Count a5,
                                      MPI_Datatype a6,
                                      MPI_Comm a7,
                                      MPI_Request *a8)
{
  PyMPI_WEAK_CALL(MPI_Ineighbor_alltoall_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Ineighbor_alltoall(a1, b2, a3, a4, b5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ineighbor_alltoall_c
#define MPI_Ineighbor_alltoall_c PyMPI_Ineighbor_alltoall_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ineighbor_alltoallv_c) || PyMPI_LEGACY_ABI
#undef MPI_Ineighbor_alltoallv_c
static int PyMPI_Ineighbor_alltoallv_c(void *a1,
                                       MPI_Count *a2,
                                       MPI_Aint *a3,
                                       MPI_Datatype a4,
                                       void *a5,
                                       MPI_Count *a6,
                                       MPI_Aint *a7,
                                       MPI_Datatype a8,
                                       MPI_Comm a9,
                                       MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Ineighbor_alltoallv_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr; int ns, nr;
  int *b2 = NULL; int *b3 = NULL; int *b6 = NULL; int *b7 = NULL;
  PyMPICommNeighborCount(a9, ns, nr);
  PyMPICastArray(int, b2, MPI_Count, a2, ns);
  PyMPIMoveArray(int, b2, MPI_Count, a2, ns);
  PyMPICastArray(int, b3, MPI_Aint, a3, ns);
  PyMPIMoveArray(int, b3, MPI_Aint, a3, ns);
  PyMPICastArray(int, b6, MPI_Count, a6, nr);
  PyMPIMoveArray(int, b6, MPI_Count, a6, nr);
  PyMPICastArray(int, b7, MPI_Aint, a7, nr);
  PyMPIMoveArray(int, b7, MPI_Aint, a7, nr);
  ierr = MPI_Ineighbor_alltoallv(a1, b2, b3, a4, a5, b6, b7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ineighbor_alltoallv_c
#define MPI_Ineighbor_alltoallv_c PyMPI_Ineighbor_alltoallv_c
#endif

#if !defined(PyMPI_HAVE_MPI_Ineighbor_alltoallw_c) || PyMPI_LEGACY_ABI
#undef MPI_Ineighbor_alltoallw_c
static int PyMPI_Ineighbor_alltoallw_c(void *a1,
                                       MPI_Count *a2,
                                       MPI_Aint *a3,
                                       MPI_Datatype *a4,
                                       void *a5,
                                       MPI_Count *a6,
                                       MPI_Aint *a7,
                                       MPI_Datatype *a8,
                                       MPI_Comm a9,
                                       MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Ineighbor_alltoallw_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr; int ns, nr;
  int *b2 = NULL; int *b6 = NULL;
  PyMPICommNeighborCount(a9, ns, nr);
  PyMPICastArray(int, b2, MPI_Count, a2, ns);
  PyMPIMoveArray(int, b2, MPI_Count, a2, ns);
  PyMPICastArray(int, b6, MPI_Count, a6, nr);
  PyMPIMoveArray(int, b6, MPI_Count, a6, nr);
  ierr = MPI_Ineighbor_alltoallw(a1, b2, a3, a4, a5, b6, a7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Ineighbor_alltoallw_c
#define MPI_Ineighbor_alltoallw_c PyMPI_Ineighbor_alltoallw_c
#endif

#if !defined(PyMPI_HAVE_MPI_Bcast_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Bcast_init_c
static int PyMPI_Bcast_init_c(void *a1,
                              MPI_Count a2,
                              MPI_Datatype a3,
                              int a4,
                              MPI_Comm a5,
                              MPI_Info a6,
                              MPI_Request *a7)
{
  PyMPI_WEAK_CALL(MPI_Bcast_init_c, a1, a2, a3, a4, a5, a6, a7);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Count, a2);
  ierr = MPI_Bcast_init(a1, b2, a3, a4, a5, a6, a7);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Bcast_init_c
#define MPI_Bcast_init_c PyMPI_Bcast_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Gather_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Gather_init_c
static int PyMPI_Gather_init_c(void *a1,
                               MPI_Count a2,
                               MPI_Datatype a3,
                               void *a4,
                               MPI_Count a5,
                               MPI_Datatype a6,
                               int a7,
                               MPI_Comm a8,
                               MPI_Info a9,
                               MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Gather_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Gather_init(a1, b2, a3, a4, b5, a6, a7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Gather_init_c
#define MPI_Gather_init_c PyMPI_Gather_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Gatherv_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Gatherv_init_c
static int PyMPI_Gatherv_init_c(void *a1,
                                MPI_Count a2,
                                MPI_Datatype a3,
                                void *a4,
                                MPI_Count *a5,
                                MPI_Aint *a6,
                                MPI_Datatype a7,
                                int a8,
                                MPI_Comm a9,
                                MPI_Info a10,
                                MPI_Request *a11)
{
  PyMPI_WEAK_CALL(MPI_Gatherv_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11);
  {
  int ierr; int n;
  int b2; int *b5 = NULL; int *b6 = NULL;
  PyMPICommSize(a9, n);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(int, b5, MPI_Count, a5, n);
  PyMPICastArray(int, b6, MPI_Aint, a6, n);
  ierr = MPI_Gatherv_init(a1, b2, a3, a4, b5, b6, a7, a8, a9, a10, a11);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b5);
  PyMPIFreeArray(b6);
  return ierr;
  }
}
#undef  MPI_Gatherv_init_c
#define MPI_Gatherv_init_c PyMPI_Gatherv_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Scatter_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Scatter_init_c
static int PyMPI_Scatter_init_c(void *a1,
                                MPI_Count a2,
                                MPI_Datatype a3,
                                void *a4,
                                MPI_Count a5,
                                MPI_Datatype a6,
                                int a7,
                                MPI_Comm a8,
                                MPI_Info a9,
                                MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Scatter_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Scatter_init(a1, b2, a3, a4, b5, a6, a7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Scatter_init_c
#define MPI_Scatter_init_c PyMPI_Scatter_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Scatterv_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Scatterv_init_c
static int PyMPI_Scatterv_init_c(void *a1,
                                 MPI_Count *a2,
                                 MPI_Aint *a3,
                                 MPI_Datatype a4,
                                 void *a5,
                                 MPI_Count a6,
                                 MPI_Datatype a7,
                                 int a8,
                                 MPI_Comm a9,
                                 MPI_Info a10,
                                 MPI_Request *a11)
{
  PyMPI_WEAK_CALL(MPI_Scatterv_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11);
  {
  int ierr; int n;
  int *b2 = NULL; int *b3 = NULL; int b6;
  PyMPICommSize(a9, n);
  PyMPICastArray(int, b2, MPI_Count, a2, n);
  PyMPICastArray(int, b3, MPI_Aint, a3, n);
  PyMPICastValue(int, b6, MPI_Count, a6);
  ierr = MPI_Scatterv_init(a1, b2, b3, a4, a5, b6, a7, a8, a9, a10, a11);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  return ierr;
  }
}
#undef  MPI_Scatterv_init_c
#define MPI_Scatterv_init_c PyMPI_Scatterv_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Allgather_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Allgather_init_c
static int PyMPI_Allgather_init_c(void *a1,
                                  MPI_Count a2,
                                  MPI_Datatype a3,
                                  void *a4,
                                  MPI_Count a5,
                                  MPI_Datatype a6,
                                  MPI_Comm a7,
                                  MPI_Info a8,
                                  MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Allgather_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Allgather_init(a1, b2, a3, a4, b5, a6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Allgather_init_c
#define MPI_Allgather_init_c PyMPI_Allgather_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Allgatherv_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Allgatherv_init_c
static int PyMPI_Allgatherv_init_c(void *a1,
                                   MPI_Count a2,
                                   MPI_Datatype a3,
                                   void *a4,
                                   MPI_Count *a5,
                                   MPI_Aint *a6,
                                   MPI_Datatype a7,
                                   MPI_Comm a8,
                                   MPI_Info a9,
                                   MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Allgatherv_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr; int n;
  int b2; int *b5 = NULL; int *b6 = NULL;
  PyMPICommSize(a8, n);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(int, b5, MPI_Count, a5, n);
  PyMPICastArray(int, b6, MPI_Aint, a6, n);
  ierr = MPI_Allgatherv_init(a1, b2, a3, a4, b5, b6, a7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b5);
  PyMPIFreeArray(b6);
  return ierr;
  }
}
#undef  MPI_Allgatherv_init_c
#define MPI_Allgatherv_init_c PyMPI_Allgatherv_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Alltoall_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Alltoall_init_c
static int PyMPI_Alltoall_init_c(void *a1,
                                 MPI_Count a2,
                                 MPI_Datatype a3,
                                 void *a4,
                                 MPI_Count a5,
                                 MPI_Datatype a6,
                                 MPI_Comm a7,
                                 MPI_Info a8,
                                 MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Alltoall_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Alltoall_init(a1, b2, a3, a4, b5, a6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Alltoall_init_c
#define MPI_Alltoall_init_c PyMPI_Alltoall_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Alltoallv_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Alltoallv_init_c
static int PyMPI_Alltoallv_init_c(void *a1,
                                  MPI_Count *a2,
                                  MPI_Aint *a3,
                                  MPI_Datatype a4,
                                  void *a5,
                                  MPI_Count *a6,
                                  MPI_Aint *a7,
                                  MPI_Datatype a8,
                                  MPI_Comm a9,
                                  MPI_Info a10,
                                  MPI_Request *a11)
{
  PyMPI_WEAK_CALL(MPI_Alltoallv_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11);
  {
  int ierr; int n;
  int *b2 = NULL; int *b3 = NULL; int *b6 = NULL; int *b7 = NULL;
  PyMPICommSize(a9, n);
  PyMPICastArray(int, b2, MPI_Count, a2, n);
  PyMPICastArray(int, b3, MPI_Aint, a3, n);
  PyMPICastArray(int, b6, MPI_Count, a6, n);
  PyMPICastArray(int, b7, MPI_Aint, a7, n);
  ierr = MPI_Alltoallv_init(a1, b2, b3, a4, a5, b6, b7, a8, a9, a10, a11);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  PyMPIFreeArray(b6);
  PyMPIFreeArray(b7);
  return ierr;
  }
}
#undef  MPI_Alltoallv_init_c
#define MPI_Alltoallv_init_c PyMPI_Alltoallv_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Alltoallw_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Alltoallw_init_c
static int PyMPI_Alltoallw_init_c(void *a1,
                                  MPI_Count *a2,
                                  MPI_Aint *a3,
                                  MPI_Datatype *a4,
                                  void *a5,
                                  MPI_Count *a6,
                                  MPI_Aint *a7,
                                  MPI_Datatype *a8,
                                  MPI_Comm a9,
                                  MPI_Info a10,
                                  MPI_Request *a11)
{
  PyMPI_WEAK_CALL(MPI_Alltoallw_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11);
  {
  int ierr; int n;
  int *b2 = NULL; int *b3 = NULL; int *b6 = NULL; int *b7 = NULL;
  PyMPICommSize(a9, n);
  PyMPICastArray(int, b2, MPI_Count, a2, n);
  PyMPICastArray(int, b3, MPI_Aint, a3, n);
  PyMPICastArray(int, b6, MPI_Count, a6, n);
  PyMPICastArray(int, b7, MPI_Aint, a7, n);
  ierr = MPI_Alltoallw_init(a1, b2, b3, a4, a5, b6, b7, a8, a9, a10, a11);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  PyMPIFreeArray(b6);
  PyMPIFreeArray(b7);
  return ierr;
  }
}
#undef  MPI_Alltoallw_init_c
#define MPI_Alltoallw_init_c PyMPI_Alltoallw_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Reduce_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Reduce_init_c
static int PyMPI_Reduce_init_c(void *a1,
                               void *a2,
                               MPI_Count a3,
                               MPI_Datatype a4,
                               MPI_Op a5,
                               int a6,
                               MPI_Comm a7,
                               MPI_Info a8,
                               MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Reduce_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Reduce_init(a1, a2, b3, a4, a5, a6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Reduce_init_c
#define MPI_Reduce_init_c PyMPI_Reduce_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Allreduce_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Allreduce_init_c
static int PyMPI_Allreduce_init_c(void *a1,
                                  void *a2,
                                  MPI_Count a3,
                                  MPI_Datatype a4,
                                  MPI_Op a5,
                                  MPI_Comm a6,
                                  MPI_Info a7,
                                  MPI_Request *a8)
{
  PyMPI_WEAK_CALL(MPI_Allreduce_init_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Allreduce_init(a1, a2, b3, a4, a5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Allreduce_init_c
#define MPI_Allreduce_init_c PyMPI_Allreduce_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Reduce_scatter_block_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Reduce_scatter_block_init_c
static int PyMPI_Reduce_scatter_block_init_c(void *a1,
                                             void *a2,
                                             MPI_Count a3,
                                             MPI_Datatype a4,
                                             MPI_Op a5,
                                             MPI_Comm a6,
                                             MPI_Info a7,
                                             MPI_Request *a8)
{
  PyMPI_WEAK_CALL(MPI_Reduce_scatter_block_init_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Reduce_scatter_block_init(a1, a2, b3, a4, a5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Reduce_scatter_block_init_c
#define MPI_Reduce_scatter_block_init_c PyMPI_Reduce_scatter_block_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Reduce_scatter_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Reduce_scatter_init_c
static int PyMPI_Reduce_scatter_init_c(void *a1,
                                       void *a2,
                                       MPI_Count *a3,
                                       MPI_Datatype a4,
                                       MPI_Op a5,
                                       MPI_Comm a6,
                                       MPI_Info a7,
                                       MPI_Request *a8)
{
  PyMPI_WEAK_CALL(MPI_Reduce_scatter_init_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr; int n;
  int *b3 = NULL;
  PyMPICommLocalGroupSize(a6, n);
  PyMPICastArray(int, b3, MPI_Count, a3, n);
  ierr = MPI_Reduce_scatter_init(a1, a2, b3, a4, a5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b3);
  return ierr;
  }
}
#undef  MPI_Reduce_scatter_init_c
#define MPI_Reduce_scatter_init_c PyMPI_Reduce_scatter_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Scan_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Scan_init_c
static int PyMPI_Scan_init_c(void *a1,
                             void *a2,
                             MPI_Count a3,
                             MPI_Datatype a4,
                             MPI_Op a5,
                             MPI_Comm a6,
                             MPI_Info a7,
                             MPI_Request *a8)
{
  PyMPI_WEAK_CALL(MPI_Scan_init_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Scan_init(a1, a2, b3, a4, a5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Scan_init_c
#define MPI_Scan_init_c PyMPI_Scan_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Exscan_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Exscan_init_c
static int PyMPI_Exscan_init_c(void *a1,
                               void *a2,
                               MPI_Count a3,
                               MPI_Datatype a4,
                               MPI_Op a5,
                               MPI_Comm a6,
                               MPI_Info a7,
                               MPI_Request *a8)
{
  PyMPI_WEAK_CALL(MPI_Exscan_init_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_Exscan_init(a1, a2, b3, a4, a5, a6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Exscan_init_c
#define MPI_Exscan_init_c PyMPI_Exscan_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Neighbor_allgather_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Neighbor_allgather_init_c
static int PyMPI_Neighbor_allgather_init_c(void *a1,
                                           MPI_Count a2,
                                           MPI_Datatype a3,
                                           void *a4,
                                           MPI_Count a5,
                                           MPI_Datatype a6,
                                           MPI_Comm a7,
                                           MPI_Info a8,
                                           MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Neighbor_allgather_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Neighbor_allgather_init(a1, b2, a3, a4, b5, a6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Neighbor_allgather_init_c
#define MPI_Neighbor_allgather_init_c PyMPI_Neighbor_allgather_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Neighbor_allgatherv_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Neighbor_allgatherv_init_c
static int PyMPI_Neighbor_allgatherv_init_c(void *a1,
                                            MPI_Count a2,
                                            MPI_Datatype a3,
                                            void *a4,
                                            MPI_Count *a5,
                                            MPI_Aint *a6,
                                            MPI_Datatype a7,
                                            MPI_Comm a8,
                                            MPI_Info a9,
                                            MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Neighbor_allgatherv_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr; int ns, nr;
  int b2; int *b5 = NULL; int *b6 = NULL;
  PyMPICommNeighborCount(a8, ns, nr);
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastArray(int, b5, MPI_Count, a5, nr);
  PyMPICastArray(int, b6, MPI_Aint, a6, nr);
  ierr = MPI_Neighbor_allgatherv_init(a1, b2, a3, a4, b5, b6, a7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b5);
  PyMPIFreeArray(b6);
  return ierr;
  }
}
#undef  MPI_Neighbor_allgatherv_init_c
#define MPI_Neighbor_allgatherv_init_c PyMPI_Neighbor_allgatherv_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Neighbor_alltoall_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Neighbor_alltoall_init_c
static int PyMPI_Neighbor_alltoall_init_c(void *a1,
                                          MPI_Count a2,
                                          MPI_Datatype a3,
                                          void *a4,
                                          MPI_Count a5,
                                          MPI_Datatype a6,
                                          MPI_Comm a7,
                                          MPI_Info a8,
                                          MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Neighbor_alltoall_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2; int b5;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  ierr = MPI_Neighbor_alltoall_init(a1, b2, a3, a4, b5, a6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Neighbor_alltoall_init_c
#define MPI_Neighbor_alltoall_init_c PyMPI_Neighbor_alltoall_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Neighbor_alltoallv_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Neighbor_alltoallv_init_c
static int PyMPI_Neighbor_alltoallv_init_c(void *a1,
                                           MPI_Count *a2,
                                           MPI_Aint *a3,
                                           MPI_Datatype a4,
                                           void *a5,
                                           MPI_Count *a6,
                                           MPI_Aint *a7,
                                           MPI_Datatype a8,
                                           MPI_Comm a9,
                                           MPI_Info a10,
                                           MPI_Request *a11)
{
  PyMPI_WEAK_CALL(MPI_Neighbor_alltoallv_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11);
  {
  int ierr; int ns, nr;
  int *b2 = NULL; int *b3 = NULL; int *b6 = NULL; int *b7 = NULL;
  PyMPICommNeighborCount(a9, ns, nr);
  PyMPICastArray(int, b2, MPI_Count, a2, ns);
  PyMPICastArray(int, b3, MPI_Aint, a3, ns);
  PyMPICastArray(int, b6, MPI_Count, a6, nr);
  PyMPICastArray(int, b7, MPI_Aint, a7, nr);
  ierr = MPI_Neighbor_alltoallv_init(a1, b2, b3, a4, a5, b6, b7, a8, a9, a10, a11);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b3);
  PyMPIFreeArray(b6);
  PyMPIFreeArray(b7);
  return ierr;
  }
}
#undef  MPI_Neighbor_alltoallv_init_c
#define MPI_Neighbor_alltoallv_init_c PyMPI_Neighbor_alltoallv_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Neighbor_alltoallw_init_c) || PyMPI_LEGACY_ABI
#undef MPI_Neighbor_alltoallw_init_c
static int PyMPI_Neighbor_alltoallw_init_c(void *a1,
                                           MPI_Count *a2,
                                           MPI_Aint *a3,
                                           MPI_Datatype *a4,
                                           void *a5,
                                           MPI_Count *a6,
                                           MPI_Aint *a7,
                                           MPI_Datatype *a8,
                                           MPI_Comm a9,
                                           MPI_Info a10,
                                           MPI_Request *a11)
{
  PyMPI_WEAK_CALL(MPI_Neighbor_alltoallw_init_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11);
  {
  int ierr; int ns, nr;
  int *b2 = NULL; int *b6 = NULL;
  PyMPICommNeighborCount(a9, ns, nr);
  PyMPICastArray(int, b2, MPI_Count, a2, ns);
  PyMPICastArray(int, b6, MPI_Count, a6, nr);
  ierr = MPI_Neighbor_alltoallw_init(a1, b2, a3, a4, a5, b6, a7, a8, a9, a10, a11);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  PyMPIFreeArray(b2);
  PyMPIFreeArray(b6);
  return ierr;
  }
}
#undef  MPI_Neighbor_alltoallw_init_c
#define MPI_Neighbor_alltoallw_init_c PyMPI_Neighbor_alltoallw_init_c
#endif

#if !defined(PyMPI_HAVE_MPI_Win_create_c) || PyMPI_LEGACY_ABI
#undef MPI_Win_create_c
static int PyMPI_Win_create_c(void *a1,
                              MPI_Aint a2,
                              MPI_Aint a3,
                              MPI_Info a4,
                              MPI_Comm a5,
                              MPI_Win *a6)
{
  PyMPI_WEAK_CALL(MPI_Win_create_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Aint, a3);
  ierr = MPI_Win_create(a1, a2, b3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Win_create_c
#define MPI_Win_create_c PyMPI_Win_create_c
#endif

#if !defined(PyMPI_HAVE_MPI_Win_allocate_c) || PyMPI_LEGACY_ABI
#undef MPI_Win_allocate_c
static int PyMPI_Win_allocate_c(MPI_Aint a1,
                                MPI_Aint a2,
                                MPI_Info a3,
                                MPI_Comm a4,
                                void *a5,
                                MPI_Win *a6)
{
  PyMPI_WEAK_CALL(MPI_Win_allocate_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Aint, a2);
  ierr = MPI_Win_allocate(a1, b2, a3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Win_allocate_c
#define MPI_Win_allocate_c PyMPI_Win_allocate_c
#endif

#if !defined(PyMPI_HAVE_MPI_Win_allocate_shared_c) || PyMPI_LEGACY_ABI
#undef MPI_Win_allocate_shared_c
static int PyMPI_Win_allocate_shared_c(MPI_Aint a1,
                                       MPI_Aint a2,
                                       MPI_Info a3,
                                       MPI_Comm a4,
                                       void *a5,
                                       MPI_Win *a6)
{
  PyMPI_WEAK_CALL(MPI_Win_allocate_shared_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b2;
  PyMPICastValue(int, b2, MPI_Aint, a2);
  ierr = MPI_Win_allocate_shared(a1, b2, a3, a4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Win_allocate_shared_c
#define MPI_Win_allocate_shared_c PyMPI_Win_allocate_shared_c
#endif

#if !defined(PyMPI_HAVE_MPI_Win_shared_query_c) || PyMPI_LEGACY_ABI
#undef MPI_Win_shared_query_c
static int PyMPI_Win_shared_query_c(MPI_Win a1,
                                    int a2,
                                    MPI_Aint *a3,
                                    MPI_Aint *a4,
                                    void *a5)
{
  PyMPI_WEAK_CALL(MPI_Win_shared_query_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b4 = 0; int *p4 = a4 ? &b4 : NULL;
  ierr = MPI_Win_shared_query(a1, a2, a3, p4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a4) *a4 = b4;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Win_shared_query_c
#define MPI_Win_shared_query_c PyMPI_Win_shared_query_c
#endif

#if !defined(PyMPI_HAVE_MPI_Get_c) || PyMPI_LEGACY_ABI
#undef MPI_Get_c
static int PyMPI_Get_c(void *a1,
                       MPI_Count a2,
                       MPI_Datatype a3,
                       int a4,
                       MPI_Aint a5,
                       MPI_Count a6,
                       MPI_Datatype a7,
                       MPI_Win a8)
{
  PyMPI_WEAK_CALL(MPI_Get_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b2; int b6;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b6, MPI_Count, a6);
  ierr = MPI_Get(a1, b2, a3, a4, a5, b6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Get_c
#define MPI_Get_c PyMPI_Get_c
#endif

#if !defined(PyMPI_HAVE_MPI_Put_c) || PyMPI_LEGACY_ABI
#undef MPI_Put_c
static int PyMPI_Put_c(void *a1,
                       MPI_Count a2,
                       MPI_Datatype a3,
                       int a4,
                       MPI_Aint a5,
                       MPI_Count a6,
                       MPI_Datatype a7,
                       MPI_Win a8)
{
  PyMPI_WEAK_CALL(MPI_Put_c, a1, a2, a3, a4, a5, a6, a7, a8);
  {
  int ierr;
  int b2; int b6;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b6, MPI_Count, a6);
  ierr = MPI_Put(a1, b2, a3, a4, a5, b6, a7, a8);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Put_c
#define MPI_Put_c PyMPI_Put_c
#endif

#if !defined(PyMPI_HAVE_MPI_Accumulate_c) || PyMPI_LEGACY_ABI
#undef MPI_Accumulate_c
static int PyMPI_Accumulate_c(void *a1,
                              MPI_Count a2,
                              MPI_Datatype a3,
                              int a4,
                              MPI_Aint a5,
                              MPI_Count a6,
                              MPI_Datatype a7,
                              MPI_Op a8,
                              MPI_Win a9)
{
  PyMPI_WEAK_CALL(MPI_Accumulate_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2; int b6;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b6, MPI_Count, a6);
  ierr = MPI_Accumulate(a1, b2, a3, a4, a5, b6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Accumulate_c
#define MPI_Accumulate_c PyMPI_Accumulate_c
#endif

#if !defined(PyMPI_HAVE_MPI_Get_accumulate_c) || PyMPI_LEGACY_ABI
#undef MPI_Get_accumulate_c
static int PyMPI_Get_accumulate_c(void *a1,
                                  MPI_Count a2,
                                  MPI_Datatype a3,
                                  void *a4,
                                  MPI_Count a5,
                                  MPI_Datatype a6,
                                  int a7,
                                  MPI_Aint a8,
                                  MPI_Count a9,
                                  MPI_Datatype a10,
                                  MPI_Op a11,
                                  MPI_Win a12)
{
  PyMPI_WEAK_CALL(MPI_Get_accumulate_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12);
  {
  int ierr;
  int b2; int b5; int b9;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  PyMPICastValue(int, b9, MPI_Count, a9);
  ierr = MPI_Get_accumulate(a1, b2, a3, a4, b5, a6, a7, a8, b9, a10, a11, a12);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Get_accumulate_c
#define MPI_Get_accumulate_c PyMPI_Get_accumulate_c
#endif

#if !defined(PyMPI_HAVE_MPI_Rget_c) || PyMPI_LEGACY_ABI
#undef MPI_Rget_c
static int PyMPI_Rget_c(void *a1,
                        MPI_Count a2,
                        MPI_Datatype a3,
                        int a4,
                        MPI_Aint a5,
                        MPI_Count a6,
                        MPI_Datatype a7,
                        MPI_Win a8,
                        MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Rget_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2; int b6;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b6, MPI_Count, a6);
  ierr = MPI_Rget(a1, b2, a3, a4, a5, b6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Rget_c
#define MPI_Rget_c PyMPI_Rget_c
#endif

#if !defined(PyMPI_HAVE_MPI_Rput_c) || PyMPI_LEGACY_ABI
#undef MPI_Rput_c
static int PyMPI_Rput_c(void *a1,
                        MPI_Count a2,
                        MPI_Datatype a3,
                        int a4,
                        MPI_Aint a5,
                        MPI_Count a6,
                        MPI_Datatype a7,
                        MPI_Win a8,
                        MPI_Request *a9)
{
  PyMPI_WEAK_CALL(MPI_Rput_c, a1, a2, a3, a4, a5, a6, a7, a8, a9);
  {
  int ierr;
  int b2; int b6;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b6, MPI_Count, a6);
  ierr = MPI_Rput(a1, b2, a3, a4, a5, b6, a7, a8, a9);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Rput_c
#define MPI_Rput_c PyMPI_Rput_c
#endif

#if !defined(PyMPI_HAVE_MPI_Raccumulate_c) || PyMPI_LEGACY_ABI
#undef MPI_Raccumulate_c
static int PyMPI_Raccumulate_c(void *a1,
                               MPI_Count a2,
                               MPI_Datatype a3,
                               int a4,
                               MPI_Aint a5,
                               MPI_Count a6,
                               MPI_Datatype a7,
                               MPI_Op a8,
                               MPI_Win a9,
                               MPI_Request *a10)
{
  PyMPI_WEAK_CALL(MPI_Raccumulate_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10);
  {
  int ierr;
  int b2; int b6;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b6, MPI_Count, a6);
  ierr = MPI_Raccumulate(a1, b2, a3, a4, a5, b6, a7, a8, a9, a10);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Raccumulate_c
#define MPI_Raccumulate_c PyMPI_Raccumulate_c
#endif

#if !defined(PyMPI_HAVE_MPI_Rget_accumulate_c) || PyMPI_LEGACY_ABI
#undef MPI_Rget_accumulate_c
static int PyMPI_Rget_accumulate_c(void *a1,
                                   MPI_Count a2,
                                   MPI_Datatype a3,
                                   void *a4,
                                   MPI_Count a5,
                                   MPI_Datatype a6,
                                   int a7,
                                   MPI_Aint a8,
                                   MPI_Count a9,
                                   MPI_Datatype a10,
                                   MPI_Op a11,
                                   MPI_Win a12,
                                   MPI_Request *a13)
{
  PyMPI_WEAK_CALL(MPI_Rget_accumulate_c, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13);
  {
  int ierr;
  int b2; int b5; int b9;
  PyMPICastValue(int, b2, MPI_Count, a2);
  PyMPICastValue(int, b5, MPI_Count, a5);
  PyMPICastValue(int, b9, MPI_Count, a9);
  ierr = MPI_Rget_accumulate(a1, b2, a3, a4, b5, a6, a7, a8, b9, a10, a11, a12, a13);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_Rget_accumulate_c
#define MPI_Rget_accumulate_c PyMPI_Rget_accumulate_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_read_at_c) || PyMPI_LEGACY_ABI
#undef MPI_File_read_at_c
static int PyMPI_File_read_at_c(MPI_File a1,
                                MPI_Offset a2,
                                void *a3,
                                MPI_Count a4,
                                MPI_Datatype a5,
                                MPI_Status *a6)
{
  PyMPI_WEAK_CALL(MPI_File_read_at_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b4;
  PyMPICastValue(int, b4, MPI_Count, a4);
  ierr = MPI_File_read_at(a1, a2, a3, b4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_read_at_c
#define MPI_File_read_at_c PyMPI_File_read_at_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_read_at_all_c) || PyMPI_LEGACY_ABI
#undef MPI_File_read_at_all_c
static int PyMPI_File_read_at_all_c(MPI_File a1,
                                    MPI_Offset a2,
                                    void *a3,
                                    MPI_Count a4,
                                    MPI_Datatype a5,
                                    MPI_Status *a6)
{
  PyMPI_WEAK_CALL(MPI_File_read_at_all_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b4;
  PyMPICastValue(int, b4, MPI_Count, a4);
  ierr = MPI_File_read_at_all(a1, a2, a3, b4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_read_at_all_c
#define MPI_File_read_at_all_c PyMPI_File_read_at_all_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_write_at_c) || PyMPI_LEGACY_ABI
#undef MPI_File_write_at_c
static int PyMPI_File_write_at_c(MPI_File a1,
                                 MPI_Offset a2,
                                 void *a3,
                                 MPI_Count a4,
                                 MPI_Datatype a5,
                                 MPI_Status *a6)
{
  PyMPI_WEAK_CALL(MPI_File_write_at_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b4;
  PyMPICastValue(int, b4, MPI_Count, a4);
  ierr = MPI_File_write_at(a1, a2, a3, b4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_write_at_c
#define MPI_File_write_at_c PyMPI_File_write_at_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_write_at_all_c) || PyMPI_LEGACY_ABI
#undef MPI_File_write_at_all_c
static int PyMPI_File_write_at_all_c(MPI_File a1,
                                     MPI_Offset a2,
                                     void *a3,
                                     MPI_Count a4,
                                     MPI_Datatype a5,
                                     MPI_Status *a6)
{
  PyMPI_WEAK_CALL(MPI_File_write_at_all_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b4;
  PyMPICastValue(int, b4, MPI_Count, a4);
  ierr = MPI_File_write_at_all(a1, a2, a3, b4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_write_at_all_c
#define MPI_File_write_at_all_c PyMPI_File_write_at_all_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_iread_at_c) || PyMPI_LEGACY_ABI
#undef MPI_File_iread_at_c
static int PyMPI_File_iread_at_c(MPI_File a1,
                                 MPI_Offset a2,
                                 void *a3,
                                 MPI_Count a4,
                                 MPI_Datatype a5,
                                 MPI_Request *a6)
{
  PyMPI_WEAK_CALL(MPI_File_iread_at_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b4;
  PyMPICastValue(int, b4, MPI_Count, a4);
  ierr = MPI_File_iread_at(a1, a2, a3, b4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_iread_at_c
#define MPI_File_iread_at_c PyMPI_File_iread_at_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_iread_at_all_c) || PyMPI_LEGACY_ABI
#undef MPI_File_iread_at_all_c
static int PyMPI_File_iread_at_all_c(MPI_File a1,
                                     MPI_Offset a2,
                                     void *a3,
                                     MPI_Count a4,
                                     MPI_Datatype a5,
                                     MPI_Request *a6)
{
  PyMPI_WEAK_CALL(MPI_File_iread_at_all_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b4;
  PyMPICastValue(int, b4, MPI_Count, a4);
  ierr = MPI_File_iread_at_all(a1, a2, a3, b4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_iread_at_all_c
#define MPI_File_iread_at_all_c PyMPI_File_iread_at_all_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_iwrite_at_c) || PyMPI_LEGACY_ABI
#undef MPI_File_iwrite_at_c
static int PyMPI_File_iwrite_at_c(MPI_File a1,
                                  MPI_Offset a2,
                                  void *a3,
                                  MPI_Count a4,
                                  MPI_Datatype a5,
                                  MPI_Request *a6)
{
  PyMPI_WEAK_CALL(MPI_File_iwrite_at_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b4;
  PyMPICastValue(int, b4, MPI_Count, a4);
  ierr = MPI_File_iwrite_at(a1, a2, a3, b4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_iwrite_at_c
#define MPI_File_iwrite_at_c PyMPI_File_iwrite_at_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_iwrite_at_all_c) || PyMPI_LEGACY_ABI
#undef MPI_File_iwrite_at_all_c
static int PyMPI_File_iwrite_at_all_c(MPI_File a1,
                                      MPI_Offset a2,
                                      void *a3,
                                      MPI_Count a4,
                                      MPI_Datatype a5,
                                      MPI_Request *a6)
{
  PyMPI_WEAK_CALL(MPI_File_iwrite_at_all_c, a1, a2, a3, a4, a5, a6);
  {
  int ierr;
  int b4;
  PyMPICastValue(int, b4, MPI_Count, a4);
  ierr = MPI_File_iwrite_at_all(a1, a2, a3, b4, a5, a6);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_iwrite_at_all_c
#define MPI_File_iwrite_at_all_c PyMPI_File_iwrite_at_all_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_read_c) || PyMPI_LEGACY_ABI
#undef MPI_File_read_c
static int PyMPI_File_read_c(MPI_File a1,
                             void *a2,
                             MPI_Count a3,
                             MPI_Datatype a4,
                             MPI_Status *a5)
{
  PyMPI_WEAK_CALL(MPI_File_read_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_read(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_read_c
#define MPI_File_read_c PyMPI_File_read_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_read_all_c) || PyMPI_LEGACY_ABI
#undef MPI_File_read_all_c
static int PyMPI_File_read_all_c(MPI_File a1,
                                 void *a2,
                                 MPI_Count a3,
                                 MPI_Datatype a4,
                                 MPI_Status *a5)
{
  PyMPI_WEAK_CALL(MPI_File_read_all_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_read_all(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_read_all_c
#define MPI_File_read_all_c PyMPI_File_read_all_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_write_c) || PyMPI_LEGACY_ABI
#undef MPI_File_write_c
static int PyMPI_File_write_c(MPI_File a1,
                              void *a2,
                              MPI_Count a3,
                              MPI_Datatype a4,
                              MPI_Status *a5)
{
  PyMPI_WEAK_CALL(MPI_File_write_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_write(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_write_c
#define MPI_File_write_c PyMPI_File_write_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_write_all_c) || PyMPI_LEGACY_ABI
#undef MPI_File_write_all_c
static int PyMPI_File_write_all_c(MPI_File a1,
                                  void *a2,
                                  MPI_Count a3,
                                  MPI_Datatype a4,
                                  MPI_Status *a5)
{
  PyMPI_WEAK_CALL(MPI_File_write_all_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_write_all(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_write_all_c
#define MPI_File_write_all_c PyMPI_File_write_all_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_iread_c) || PyMPI_LEGACY_ABI
#undef MPI_File_iread_c
static int PyMPI_File_iread_c(MPI_File a1,
                              void *a2,
                              MPI_Count a3,
                              MPI_Datatype a4,
                              MPI_Request *a5)
{
  PyMPI_WEAK_CALL(MPI_File_iread_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_iread(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_iread_c
#define MPI_File_iread_c PyMPI_File_iread_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_iread_all_c) || PyMPI_LEGACY_ABI
#undef MPI_File_iread_all_c
static int PyMPI_File_iread_all_c(MPI_File a1,
                                  void *a2,
                                  MPI_Count a3,
                                  MPI_Datatype a4,
                                  MPI_Request *a5)
{
  PyMPI_WEAK_CALL(MPI_File_iread_all_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_iread_all(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_iread_all_c
#define MPI_File_iread_all_c PyMPI_File_iread_all_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_iwrite_c) || PyMPI_LEGACY_ABI
#undef MPI_File_iwrite_c
static int PyMPI_File_iwrite_c(MPI_File a1,
                               void *a2,
                               MPI_Count a3,
                               MPI_Datatype a4,
                               MPI_Request *a5)
{
  PyMPI_WEAK_CALL(MPI_File_iwrite_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_iwrite(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_iwrite_c
#define MPI_File_iwrite_c PyMPI_File_iwrite_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_iwrite_all_c) || PyMPI_LEGACY_ABI
#undef MPI_File_iwrite_all_c
static int PyMPI_File_iwrite_all_c(MPI_File a1,
                                   void *a2,
                                   MPI_Count a3,
                                   MPI_Datatype a4,
                                   MPI_Request *a5)
{
  PyMPI_WEAK_CALL(MPI_File_iwrite_all_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_iwrite_all(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_iwrite_all_c
#define MPI_File_iwrite_all_c PyMPI_File_iwrite_all_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_read_shared_c) || PyMPI_LEGACY_ABI
#undef MPI_File_read_shared_c
static int PyMPI_File_read_shared_c(MPI_File a1,
                                    void *a2,
                                    MPI_Count a3,
                                    MPI_Datatype a4,
                                    MPI_Status *a5)
{
  PyMPI_WEAK_CALL(MPI_File_read_shared_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_read_shared(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_read_shared_c
#define MPI_File_read_shared_c PyMPI_File_read_shared_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_write_shared_c) || PyMPI_LEGACY_ABI
#undef MPI_File_write_shared_c
static int PyMPI_File_write_shared_c(MPI_File a1,
                                     void *a2,
                                     MPI_Count a3,
                                     MPI_Datatype a4,
                                     MPI_Status *a5)
{
  PyMPI_WEAK_CALL(MPI_File_write_shared_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_write_shared(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_write_shared_c
#define MPI_File_write_shared_c PyMPI_File_write_shared_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_iread_shared_c) || PyMPI_LEGACY_ABI
#undef MPI_File_iread_shared_c
static int PyMPI_File_iread_shared_c(MPI_File a1,
                                     void *a2,
                                     MPI_Count a3,
                                     MPI_Datatype a4,
                                     MPI_Request *a5)
{
  PyMPI_WEAK_CALL(MPI_File_iread_shared_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_iread_shared(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_iread_shared_c
#define MPI_File_iread_shared_c PyMPI_File_iread_shared_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_iwrite_shared_c) || PyMPI_LEGACY_ABI
#undef MPI_File_iwrite_shared_c
static int PyMPI_File_iwrite_shared_c(MPI_File a1,
                                      void *a2,
                                      MPI_Count a3,
                                      MPI_Datatype a4,
                                      MPI_Request *a5)
{
  PyMPI_WEAK_CALL(MPI_File_iwrite_shared_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_iwrite_shared(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_iwrite_shared_c
#define MPI_File_iwrite_shared_c PyMPI_File_iwrite_shared_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_read_ordered_c) || PyMPI_LEGACY_ABI
#undef MPI_File_read_ordered_c
static int PyMPI_File_read_ordered_c(MPI_File a1,
                                     void *a2,
                                     MPI_Count a3,
                                     MPI_Datatype a4,
                                     MPI_Status *a5)
{
  PyMPI_WEAK_CALL(MPI_File_read_ordered_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_read_ordered(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_read_ordered_c
#define MPI_File_read_ordered_c PyMPI_File_read_ordered_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_write_ordered_c) || PyMPI_LEGACY_ABI
#undef MPI_File_write_ordered_c
static int PyMPI_File_write_ordered_c(MPI_File a1,
                                      void *a2,
                                      MPI_Count a3,
                                      MPI_Datatype a4,
                                      MPI_Status *a5)
{
  PyMPI_WEAK_CALL(MPI_File_write_ordered_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_write_ordered(a1, a2, b3, a4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_write_ordered_c
#define MPI_File_write_ordered_c PyMPI_File_write_ordered_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_read_at_all_begin_c) || PyMPI_LEGACY_ABI
#undef MPI_File_read_at_all_begin_c
static int PyMPI_File_read_at_all_begin_c(MPI_File a1,
                                          MPI_Offset a2,
                                          void *a3,
                                          MPI_Count a4,
                                          MPI_Datatype a5)
{
  PyMPI_WEAK_CALL(MPI_File_read_at_all_begin_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b4;
  PyMPICastValue(int, b4, MPI_Count, a4);
  ierr = MPI_File_read_at_all_begin(a1, a2, a3, b4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_read_at_all_begin_c
#define MPI_File_read_at_all_begin_c PyMPI_File_read_at_all_begin_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_write_at_all_begin_c) || PyMPI_LEGACY_ABI
#undef MPI_File_write_at_all_begin_c
static int PyMPI_File_write_at_all_begin_c(MPI_File a1,
                                           MPI_Offset a2,
                                           void *a3,
                                           MPI_Count a4,
                                           MPI_Datatype a5)
{
  PyMPI_WEAK_CALL(MPI_File_write_at_all_begin_c, a1, a2, a3, a4, a5);
  {
  int ierr;
  int b4;
  PyMPICastValue(int, b4, MPI_Count, a4);
  ierr = MPI_File_write_at_all_begin(a1, a2, a3, b4, a5);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_write_at_all_begin_c
#define MPI_File_write_at_all_begin_c PyMPI_File_write_at_all_begin_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_read_all_begin_c) || PyMPI_LEGACY_ABI
#undef MPI_File_read_all_begin_c
static int PyMPI_File_read_all_begin_c(MPI_File a1,
                                       void *a2,
                                       MPI_Count a3,
                                       MPI_Datatype a4)
{
  PyMPI_WEAK_CALL(MPI_File_read_all_begin_c, a1, a2, a3, a4);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_read_all_begin(a1, a2, b3, a4);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_read_all_begin_c
#define MPI_File_read_all_begin_c PyMPI_File_read_all_begin_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_write_all_begin_c) || PyMPI_LEGACY_ABI
#undef MPI_File_write_all_begin_c
static int PyMPI_File_write_all_begin_c(MPI_File a1,
                                        void *a2,
                                        MPI_Count a3,
                                        MPI_Datatype a4)
{
  PyMPI_WEAK_CALL(MPI_File_write_all_begin_c, a1, a2, a3, a4);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_write_all_begin(a1, a2, b3, a4);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_write_all_begin_c
#define MPI_File_write_all_begin_c PyMPI_File_write_all_begin_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_read_ordered_begin_c) || PyMPI_LEGACY_ABI
#undef MPI_File_read_ordered_begin_c
static int PyMPI_File_read_ordered_begin_c(MPI_File a1,
                                           void *a2,
                                           MPI_Count a3,
                                           MPI_Datatype a4)
{
  PyMPI_WEAK_CALL(MPI_File_read_ordered_begin_c, a1, a2, a3, a4);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_read_ordered_begin(a1, a2, b3, a4);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_read_ordered_begin_c
#define MPI_File_read_ordered_begin_c PyMPI_File_read_ordered_begin_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_write_ordered_begin_c) || PyMPI_LEGACY_ABI
#undef MPI_File_write_ordered_begin_c
static int PyMPI_File_write_ordered_begin_c(MPI_File a1,
                                            void *a2,
                                            MPI_Count a3,
                                            MPI_Datatype a4)
{
  PyMPI_WEAK_CALL(MPI_File_write_ordered_begin_c, a1, a2, a3, a4);
  {
  int ierr;
  int b3;
  PyMPICastValue(int, b3, MPI_Count, a3);
  ierr = MPI_File_write_ordered_begin(a1, a2, b3, a4);
  if (ierr != MPI_SUCCESS) goto fn_exit;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_write_ordered_begin_c
#define MPI_File_write_ordered_begin_c PyMPI_File_write_ordered_begin_c
#endif

#if !defined(PyMPI_HAVE_MPI_File_get_type_extent_c) || PyMPI_LEGACY_ABI
#undef MPI_File_get_type_extent_c
static int PyMPI_File_get_type_extent_c(MPI_File a1,
                                        MPI_Datatype a2,
                                        MPI_Count *a3)
{
  PyMPI_WEAK_CALL(MPI_File_get_type_extent_c, a1, a2, a3);
  {
  int ierr;
  MPI_Aint b3 = 0; MPI_Aint *p3 = a3 ? &b3 : NULL;
  ierr = MPI_File_get_type_extent(a1, a2, p3);
  if (ierr != MPI_SUCCESS) goto fn_exit;
  if (a3) *a3 = b3;
 fn_exit:
  return ierr;
  }
}
#undef  MPI_File_get_type_extent_c
#define MPI_File_get_type_extent_c PyMPI_File_get_type_extent_c
#endif

/* */
