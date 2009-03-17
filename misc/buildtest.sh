#! /bin/sh

PYTHON=python
MPIIMP=mpich2

for arg in "$@" ; do
    case "$arg" in 
    --py=*)
    PYTHON=python`echo A$arg | sed -e 's/A--py=//g'`
    ;;
    --mpi=*)
    MPIIMP=`echo A$arg | sed -e 's/A--mpi=//g'`
    ;;
    esac
done

echo ---------------------
echo Python ---- $PYTHON
echo MPI ------- $MPIIMP
echo ---------------------

BUILDDIR=/tmp/mpi4py-buildtest
VERSION=`cat VERSION.txt`
$PYTHON setup.py sdist
rm -rf $BUILDDIR && mkdir -p $BUILDDIR
cp dist/mpi4py-$VERSION.tar.gz $BUILDDIR


source misc/$MPIIMP.env
cd $BUILDDIR
tar -zxf mpi4py-$VERSION.tar.gz
cd mpi4py-$VERSION
$PYTHON setup.py install --home=$BUILDDIR
export PYTHONPATH=$BUILDDIR/lib/python:$PYTHONPATH
$MPISTARTUP
$PYTHON test/runalltest.py
sleep 3
$MPISHUTDOWN
