import dis

from garoupa import Hash
from orjson import dumps, OPT_SORT_KEYS


def process(field, value, version):
    """
    Create hash with etype=
        "hybrid" if 'value' is not callable
        "ordered" if 'value' is a callable without an attribute 'hash'

    Usage
    >>> process("X", 123, "UT64.4")

    Parameters
    ----------
    field
    value
    version

    Returns
    -------

    """
    if callable(value):
        h = value.hash if hasattr(value, "hash") else fhash(value, "ordered", version)
        return h, None
    obj = {field: value}
    bytes = dumps(obj, option=OPT_SORT_KEYS)
    return Hash(bytes, "hybrid", version=version), bytes


def fhash(f, version):
    """
    Create hash with etype="ordered" using bytecodeof "f" as binary content.

    Usage
    >>> print(fhash(lambda x: {"z": x**2}, "UT64.4"))
    3.WuJFj1LkjvzJcQXoCWvaRTfyMy71Hn0gjVZ8CMMJVv.YOSAL.a-i2dS6RIy3dO

    Parameters
    ----------
    f
    version

    Returns
    -------

    """
    return Hash(dumps(dis.Bytecode(f).dis()), "ordered", version=version)
