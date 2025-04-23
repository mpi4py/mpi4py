with open("ex-3.02.py") as source:
    exec(source.read())

count = 3
blklen = 1
stride = -2
newtype = dtype.Create_vector(count, blklen, stride)

assert newtype.size == dtype.size * count * blklen

dtype.Free()
newtype.Free()
