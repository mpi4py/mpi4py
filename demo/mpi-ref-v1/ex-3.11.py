execfile('ex-3.02.py')

B = (3, 1)
D = (4, 0)
newtype = dtype.Create_indexed(B, D)

dtype.Free()
newtype.Free()
