import dis

from garoupa import Hash
from orjson import dumps, OPT_SORT_KEYS


def process(field, value, version):
    """
    Create hash with etype=
        "hybrid" if 'value' is not callable
        "ordered" if 'value' is a callable without an attribute 'hash'

    Usage:

    >>> hash, blob = process("X", 123, "UT64.4")
    >>> hash.id
    '0000000000000000000006jfeYEWNkSX84ldc-BIj0ST9rhlkTESf81XaQdiwRPm'
    >>> blob
    b'{"X":123}'
    >>> f = lambda: 123
    >>> hasattr(f, "hash")
    False
    >>> hash, blob = process("X", f, "UT64.4")
    >>> hash.id
    'jq-fkk.Ejr0v.hOGHyBl4HaicbeEu-34uuJ8wQQNCZVqWy-YDE2Ser6JkaFjd-iH'
    >>> blob is None
    True
    >>> f.hash = hash
    >>> hasattr(f, "hash")
    True
    >>> hash2, blob = process("X", f, "UT64.4")
    >>> hash is hash2
    True

    Parameters
    ----------
    field
    value
    version

    Returns
    -------

    """
    if callable(value):
        h = value.hash if hasattr(value, "hash") else fhash(value, version)
        return h, None
    obj = {field: value}
    # TODO: separar key do hash pra ser usada como no artigo, para localizar o blob no db
    bytes = dumps(obj, option=OPT_SORT_KEYS)
    return Hash(bytes, "hybrid", version=version), bytes


def fhash(f, version):
    """
    Create hash with etype="ordered" using bytecodeof "f" as binary content.

    Usage:

    >>> print(fhash(lambda x: {"z": x**2}, "UT64.4"))
    pfwOevvOc0THi7b1R4kjIm.dfJ-YO6FPn6o5YhsOOoVNLHy4dMosf2aTkAQW5Us7

    Parameters
    ----------
    f
    version

    Returns
    -------

    """
    # Clean line numbers.
    groups = [l for l in dis.Bytecode(f).dis().split("\n\n") if l]
    clean = []
    for group in groups:
        lines = [segment for segment in group.split(" ") if segment][1:]
        clean.append(lines)

    return Hash(dumps(clean), "ordered", version=version)
