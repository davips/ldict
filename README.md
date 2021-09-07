![test](https://github.com/davips/ldict/workflows/test/badge.svg)
[![codecov](https://codecov.io/gh/davips/ldict/branch/main/graph/badge.svg)](https://codecov.io/gh/davips/ldict)

# ldict
Uniquely identified lazy dict.

[Latest version](https://github.com/davips/ldict)

## Installation
### as a standalone lib.
```bash
# Set up a virtualenv. 
python3 -m venv venv
source venv/bin/activate

# Install from PyPI...
pip install --upgrade pip
pip install -U ldict

# ...or, install from updated source code.
pip install git+https://github.com/davips/ldict
```

### from source
```bash
git clone https://github.com/davips/ldict
cd ldict
poetry install
```

## Examples
**Merging two ldicts**
<details>
<p>

```python3
from ldict import ldict

a = ldict(x=3)
print(a)
"""
{
    "id": "kr_4aee5c3bcac2c478be9901d57fd1ef8a9d002",
    "ids": "kr_4aee5c3bcac2c478be9901d57fd1ef8a9d002",
    "x": 3
}
"""
```

```python3

b = ldict(y=5)
print(b)
"""
{
    "id": "Uz_0af6d78f77734fad67e6de7cdba3ea368aae4",
    "ids": "Uz_0af6d78f77734fad67e6de7cdba3ea368aae4",
    "y": 5
}
"""
```

```python3

print(a >> b)
"""
{
    "id": "c._2b0434ca422114262680df425b85cac028be6",
    "ids": "kr_4aee5c3bcac2c478be9901d57fd1ef8a9d002 Uz_0af6d78f77734fad67e6de7cdba3ea368aae4",
    "x": 3,
    "y": 5
}
"""
```


</p>
</details>

## Features (current or planned)
* [x] 
* [ ] 

## Persistence
`poetry install -E full`

## Concept
A ldict is like a common Python dict, with extra funtionality.
It is a mapping between string keys, called fields, and any serializable object.
The ldict `id` (identifier) and the field `ids` are also part of the mapping.  

The user can provide a unique identifier ([hosh](https://pypi.org/project/garoupa))
for each function or value object.
Otherwise, they will be calculated through blake3 hashing of the content of data or bytecode of function.
For this reason, such functions should be simple, i.e.,
with minimal external dependencies, to avoid the unfortunate situation where two
functions with identical local code actually perform different calculations through
calls to external code that implement different algorithms with the same name.
Alternatively, a Hosh object can be passed inside the dict that is returned by the function, under the key "_id".

## How to use
[ongoing...]
