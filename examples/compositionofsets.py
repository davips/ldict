# Composition of sets of functions
from random import Random

from ldict import empty


# A multistep process can be defined without applying its functions


def g(x, y, a=[1, 2, 3, ..., 10], b=[0.00001, 0.0001, 0.001, ..., 100000]):
    return {"z": a * x + b * y}


def h(z, c=[1, 2, 3]):
    return {"z": c * z}


# In the ldict framework 'data is function',
# so the alias ø represents the 'empty data object' and the 'reflexive function' at the same time.
# In other words: 'inserting nothing' has the same effect as 'doing nothing'.
fun = empty >> g >> h  # empty enable the cartesian product of the subsequent sets of functions within the expression.
print(fun)
# ...

# An unnapplied function has its free parameters unsampled.
# A compostition of functions results in an ordered set (Cartesian product of sets).
# It is a set because the parameter values of the functions are still undefined.
d = {"x": 5, "y": 7} >> (Random(0) >> fun)
print(d)
# ...

print(d.z)
# ...

d = {"x": 5, "y": 7} >> (Random(0) >> fun)
print(d.z)
# ...

# Reproducible different runs by passing a stateful random number generator.
rnd = Random(0)
e = d >> rnd >> fun
print(e.z)
# ...

e = d >> rnd >> fun
print(e.z)
# ...

# Repeating the same results.
rnd = Random(0)
e = d >> rnd >> fun
print(e.z)
# ...

e = d >> rnd >> fun
print(e.z)
# ...
