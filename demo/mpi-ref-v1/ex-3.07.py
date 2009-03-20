execfile('ex-3.02.py')

count  = 2
blklen = 3
stride = 4 * dtype.extent
newtype = dtype.Create_hvector(count, blklen, stride)

assert newtype.size == dtype.size * count * blklen

dtype.Free()
newtype.Free()
