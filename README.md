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

### as an editable lib inside your project.
```bash
cd your-project
source venv/bin/activate
git clone https://github.com/davips/ldict ../ldict
pip install --upgrade pip
pip install -e ../ldict
```

## Examples
**Merging two ldicts**
<details>
<p>

```python3
from ldict import ldict

a = ldict(x=3)
b = ldict(y=5)
print(a + b)
"""
{
    "id": "0000000000000000000000hej1v389Ot74b8VUuE5X1",
    "x": 3,
    "y": 5,
    "id_*": "<hidden fields>"
}
"""
```


</p>
</details>

## Features (current or planned)

* [x] 
* [ ] 
