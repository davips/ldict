# Transparent persistence
import shelve
from collections import namedtuple
from pprint import pprint

from ldict import ldict, Ø, setup, let

# The cache can be set globally.
# It is as simple as a dict, or any dict-like implementation mapping str to serializable (pickable) content.
# Implementations can, e.g., store data on disk or in a remote computer.

setup(cache={})


def fun(x, y):
    print("Calculated!")  # Watch whether the value had to be calculated.
    return {"z": x ** y}


# The operator '^' indicates a relevant point during the process, i.e., a point where data should be stored.
# It is mostly intended to avoid costly recalculations or log results.
# The symbol points upwards, meaning data can momentarily come from or go outside of the process.
# When the same process is repeated, only the first request will trigger calculation.
# Local caching objects (dicts or dict-like database servers) can also be used.
# They should be wrapped by square brackets to avoid ambiguity.
# The list may contain many different caches, e.g.: [RAM, local, remote].
mycache = {}
remote = {}
d = Ø >> {"x": 3, "y": 2} >> fun >> [mycache, remote]
print(d)
print(d.z, d.id)
# ...

# The second request just retrieves the cached value.
d = ldict(y=2, x=3) >> fun >> [remote]
print(d.z, d.id)
# ...

# The caching operator can appear in multiple places in the expression, if intermediate values are of interest.
# The ø is used as ldict-inducer when needed.
d = ldict(y=2, x=3) >> fun ^ Ø >> (lambda x: {"x": x ** 2}) >> Ø >> {"w": 5, "k": 5} >> Ø >> [mycache]
print(d.z, d.id)
# ...

# Persisting to disk is easily done via Python shelve.
P = namedtuple("P", "x y")
a = [3, 2]
b = [1, 4]


def measure_distance(a, b):
    from math import sqrt
    return {"distance": sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)}


with shelve.open("/tmp/my-cache-file.db") as db:
    d = ldict(a=a, b=b) >> measure_distance >> [db]
    pprint(dict(db))  # Cache is initially empty.
    print(d.distance)
    pprint(dict(db))
    #  ...

    # '^' syntax is also possible.
    a = [7, 1]
    b = [4, 3]
    copy = lambda source=None, target=None, **kwargs: {target: kwargs[source]}
    mean = lambda distance, other_distance: {"m": (distance + other_distance) / 2}
    e = (
            ldict(a=a, b=b)
            >> measure_distance
            >> {"other_distance": d.distance}
            >> mean
            ^ Ø
            ^ let(source="m", target="m0")
            >> copy
            >> (lambda m: {"m": m ** 2})
    )
    e.show()
    print(e.m0, e.m)
