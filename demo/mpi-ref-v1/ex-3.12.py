execfile('ex-3.02.py')

B = (3, 1)
D = (4 * dtype.extent, 0)
newtype = dtype.Create_hindexed(B, D)

dtype.Free()
newtype.Free()
