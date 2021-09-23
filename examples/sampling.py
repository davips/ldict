# Parameterized functions and sampling
from random import Random

from ldict import Ø, let


# A function provide input fields and, optionally, parameters.
# For instance:
# 'a' is sampled from an arithmetic progression
# 'b' is sampled from a geometric progression
# Here, the syntax for default parameter values is borrowed with a new meaning.
def fun(x, y, a=[-100, -99, -98, ..., 100], b=[0.0001, 0.001, 0.01, ..., 100000000]):
    return {"z": a * x + b * y}


# Creating an empty ldict. Alternatively: d = ldict().
d = Ø >> {}
d.show(colored=False)
# ...

# Putting some values. Alternatively: d = ldict(x=5, y=7).
d["x"] = 5
d["y"] = 7
d.show(colored=False)
# ...

# Parameter values are uniformly sampled.
d1 = d >> fun
d1.show(colored=False)
print(d1.z)
# ...

d2 = d >> fun
d2.show(colored=False)
print(d2.z)
# ...

# Parameter values can also be manually set.
e = d >> let(a=5, b=10) >> fun
print(e.z)
# ...

# Not all parameters need to be set.
e = d >> let(a=5) >> fun
print(e.z)
# ...

# Each run will be a different sample for the missing parameters.
e = e >> let(a=5) >> fun
print(e.z)
# ...

# We can define the initial state of the random sampler.
# It will be in effect from its location place onwards in the expression.
e = d >> let(a=5) >> Random(0) >> fun
print(e.z)
# ...

# All runs will yield the same result,
# if starting from the same random number generator seed.
e = e >> let(a=5) >> Random(0) >> fun
print(e.z)
# ...

# Reproducible different runs are achievable by using a single random number generator.
rnd = Random(0)
e = d >> let(a=5) >> rnd >> fun
print(e.z)
e = d >> let(a=5) >> rnd >> fun  # Alternative syntax.
print(e.z)
# ...
