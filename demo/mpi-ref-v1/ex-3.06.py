execfile('ex-3.02.py')

count  = 3
blklen = 1
stride = -2
newtype = dtype.Create_vector(count, blklen, stride)

assert newtype.size == dtype.size * count * blklen

dtype.Free()
newtype.Free()
