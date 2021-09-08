# Lazily applying functions to ldict
from ldict import ldict

a = ldict(x=3)
print(a)
# ...

a = a >> ldict(y=5) >> {"z": 7} >> (lambda x, y, z: {"r": x ** y // z})
print(a)
# ...

print(a.r)
# ...

print(a)
# ...
