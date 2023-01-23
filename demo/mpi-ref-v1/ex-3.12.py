with open('ex-3.02.py') as source:
    exec(source.read())

B = (3, 1)
D = (4 * dtype.extent, 0)
newtype = dtype.Create_hindexed(B, D)

dtype.Free()
newtype.Free()
