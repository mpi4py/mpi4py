#ifndef PyMPI_MPELOG_H
#define PyMPI_MPELOG_H

typedef struct PyMPELogAPI {
  int (*Init)(void);
  int (*Finish)(const char[]);
  int (*Initialized)(void);
  int (*SyncClocks)(void);
  int (*Start)(void);
  int (*Stop)(void);
  int (*newState)(int,
		  const char[],
		  const char[],
		  const char[],
		  int[2]);
  int (*newEvent)(int,
		  const char[],
		  const char[],
		  const char[],
		  int[1]);
  int (*logEvent)(int,
		  int,
		  const char[]);
  int (*packBytes)(char[], int *,
		   char, int,
		   const void *);
} PyMPELogAPI;

extern PyMPELogAPI *PyMPELog;

#endif /*! PyMPI_MPELOG_H */
