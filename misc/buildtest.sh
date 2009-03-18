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

NAME=`$PYTHON setup.py --name`
VERSION=`$PYTHON setup.py --version`

BUILDDIR=/tmp/$NAME-buildtest
$PYTHON setup.py sdist
rm -rf $BUILDDIR && mkdir -p $BUILDDIR
cp dist/$NAME-$VERSION.tar.gz $BUILDDIR


source misc/$MPIIMP.env
cd $BUILDDIR
tar -zxf $NAME-$VERSION.tar.gz
cd $NAME-$VERSION
$PYTHON setup.py install --home=$BUILDDIR
export PYTHONPATH=$BUILDDIR/lib/python:$PYTHONPATH
$MPISTARTUP
$PYTHON test/runalltest.py
sleep 3
$MPISHUTDOWN
