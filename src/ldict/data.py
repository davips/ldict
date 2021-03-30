import dis

from garoupa import Hash
from orjson import dumps, OPT_SORT_KEYS


def process(field, data):
    if callable(data):
        obj = dis.Bytecode(data).dis()
        bytes = dumps(obj, option=OPT_SORT_KEYS)
        return Hash(bytes), None
    obj = {field: data}
    bytes = dumps(obj, option=OPT_SORT_KEYS)
    return Hash(bytes, commutative=True), bytes


def fid(f):
    return dis.Bytecode(f).dis()
