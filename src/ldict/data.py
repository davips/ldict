import dis

from garoupa import Hash
from orjson import dumps, OPT_SORT_KEYS


def process(field, value):
    if callable(value):
        h = value.hash if hasattr(value, "hash") else fhash(value)
        return h, None
    obj = {field: value}
    bytes = dumps(obj, option=OPT_SORT_KEYS)
    return Hash(bytes, commutative=True), bytes


def fhash(f):
    return Hash(dumps(dis.Bytecode(f).dis()))
