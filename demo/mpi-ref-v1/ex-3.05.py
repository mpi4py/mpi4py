with open('ex-3.02.py') as source:
    exec(source.read())

count  = 2
blklen = 3
stride = 4
newtype = dtype.Create_vector(count, blklen, stride)

assert newtype.size == dtype.size * count * blklen

dtype.Free()
newtype.Free()
