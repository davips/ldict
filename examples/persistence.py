# Transparent persistence
from ldict import ldict, ø, setcache

# The cache can be set globally.
# It is as simple as a dict, or any dict-like implementation mapping str to serializable content.
# Implementations can, e.g., store data on disk or in a remote computer.

setcache({})


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
d = ø >> {"x": 3, "y": 2} >> fun >> [mycache, remote]
print(d)
print(d.z, d.id)
# ...

# The second request just retrieves the cached value.
d = ldict(y=2, x=3) >> fun >> [remote]
print(d.z, d.id)
# ...

# The caching operator can appear in multiple places in the expression, if intermediate values are of interest.
# The ø is used as ldict-inducer when needed.
d = ldict(y=2, x=3) >> fun ^ ø >> (lambda x: {"x": x ** 2}) >> ø >> {"w": 5, "k": 5} >> ø >> [mycache]
print(d.z, d.id)
# ...
