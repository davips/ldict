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
    "id": "uRA8YjINbaaHpS1fSCh9QOAjGHk1T8YfaQ8lKavy0sy",
    "x": 3,
    "id_x": "<hidden field>"
}
"""
```

```python3

b = ldict(y=5)
print(b)
"""
{
    "id": "RooMUsgK3ZdP3bftcewZsoqbsch3bVVeeOYng8OumIa",
    "y": 5,
    "id_y": "<hidden field>"
}
"""
```

```python3

print(a + b)
"""
{
    "id": "NYEcIfLXYlefiig0Ia7A6PiLTfGRNwHZRt00Wg01692",
    "x": 3,
    "y": 5,
    "id_*": "<2 hidden fields>"
}
"""
```


</p>
</details>

## Features (current or planned)

* [x] 
* [ ] 
