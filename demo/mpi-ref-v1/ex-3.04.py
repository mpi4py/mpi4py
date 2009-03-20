execfile('ex-3.02.py')

count = 3
newtype = dtype.Create_contiguous(count)

assert newtype.extent == dtype.extent * count

dtype.Free()
newtype.Free()
