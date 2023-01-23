with open('ex-3.02.py') as source:
    exec(source.read())

count = 3
newtype = dtype.Create_contiguous(count)

assert newtype.extent == dtype.extent * count

dtype.Free()
newtype.Free()
