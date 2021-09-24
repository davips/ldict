# Laziness example
from ldict import ldict

# We disable 'ids' here just for the sake of clarity.
# setup(ids=False)

a = ldict(x=3)
print(a)
# ...

a["y"] = 5
print(a)
# ...

# Function application can be done in a stateful fashion.
# [not recommended, due to the referential transparency principle]
a["z"] = lambda x, y: x ** y
print(a)

# Function application is preferably  done through '>>' operator.
print(a >> (lambda x, y: {"z": x ** y}))
