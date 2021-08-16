import dis

from garoupa import Hosh
from orjson import dumps, OPT_SORT_KEYS


def process(field, value, version):
    """
    Create hosh with etype=
        "hybrid" if 'value' is not callable
        "ordered" if 'value' is a callable without an attribute 'hosh'

    Usage:

    >>> hosh, blob = process("X", 123, "UT64.4")
    >>> hosh.id
    '0000000000000000000006jfeYEWNkSX84ldc-BIj0ST9rhlkTESf81XaQdiwRPm'
    >>> blob
    b'{"X":123}'
    >>> f = lambda: 123
    >>> hasattr(f, "hosh")
    False
    >>> hosh, blob = process("X", f, "UT64.4")
    >>> hosh.id
    'jq-fkk.Ejr0v.hOGHyBl4HaicbeEu-34uuJ8wQQNCZVqWy-YDE2Ser6JkaFjd-iH'
    >>> blob is None
    True
    >>> f.hosh = hosh
    >>> hasattr(f, "hosh")
    True
    >>> hosh2, blob = process("X", f, "UT64.4")
    >>> hosh is hosh2
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
        h = value.hosh if hasattr(value, "hosh") else fhosh(value, version)
        return h, None
    obj = {field: value}
    # TODO: separar key do hosh pra ser usada como no artigo, para localizar o blob no db
    bytes = dumps(obj, option=OPT_SORT_KEYS)
    return Hosh(bytes, "hybrid", version=version), bytes


def fhosh(f, version):
    """
    Create hosh with etype="ordered" using bytecodeof "f" as binary content.

    Usage:

    >>> print(fhosh(lambda x: {"z": x**2}, "UT64.4"))
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

    return Hosh(dumps(clean), "ordered", version=version)
