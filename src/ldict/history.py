#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the ldict project.
#  Please respect the license - more about this in the section (*) below.
#
#  ldict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ldict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ldict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and unethical regarding the effort and
#  time spent here.


def extend_history(d, hosh):
    """
    >>> from ldict import ldict
    >>> d = ldict()
    >>> d.history
    {}
    >>> d["x"] = 5
    >>> from ldict import decolorize
    >>> decolorize(str(d.history)) == '{Tz_d158c49297834fad67e6de7cdba3ea368aae4: None}'
    True
    >>> d["y"] = 7
    >>> decolorize(str(d.history)) == '{I0_39c94b4dfbc7a8579ca1304eba25917204a5e: {Tz_d158c49297834fad67e6de7cdba3ea368aae4, Rs_92162dea64a7462725cac7dcee71b67669f69}}'
    True

    Parameters
    ----------
    d
    hosh

    Returns
    -------

    """
    if not d.history or hosh.etype == "ordered" or d.last and "_" not in d.last.id[:3]:
        d.last = hosh
        d.history[d.last] = None
    else:
        many = d.history.pop(d.last)
        previous_last = d.last
        d.last *= hosh
        if many is None:
            d.history[d.last] = {previous_last, hosh}
        else:
            many.add(hosh)
            d.history[d.last] = many


def rewrite_history(d, hosh):
    """
    >>> from ldict import ldict
    >>> d = ldict()
    >>> d["x"] = 5
    >>> del d["x"]
    >>> list(d.ids.keys()) == []
    True
    >>> d["x"] = 5
    >>> d["y"] = 7
    >>> from ldict import decolorize
    >>> decolorize(str(d.history)) == '{I0_39c94b4dfbc7a8579ca1304eba25917204a5e: {Tz_d158c49297834fad67e6de7cdba3ea368aae4, Rs_92162dea64a7462725cac7dcee71b67669f69}}'
    True
    >>> d["z"] = 8
    >>> decolorize(str(d.history)) == '{-H_b4adb0fb38e343cfe5984eec6d1c92907539b: {hH_2713d4ae3c47207859e6cd9ea2f6013e6193d, Tz_d158c49297834fad67e6de7cdba3ea368aae4, Rs_92162dea64a7462725cac7dcee71b67669f69}}'
    True
    >>> list(d.ids.keys()) == ["x", "y", "z"]
    True
    >>> del d["x"]
    >>> list(d.ids.keys()) == ["y", "z"]
    True
    >>> del d["z"]
    >>> decolorize(str(d.history)) == '{Rs_92162dea64a7462725cac7dcee71b67669f69: None}'
    True
    >>> d >>= lambda y: {"x": y**2}
    >>> d >>= lambda y: {"w": y**2}
    >>> del d["x"]
    >>> del d["w"]
    >>> decolorize(str(d.history)) == '{Rs_92162dea64a7462725cac7dcee71b67669f69: None}'
    True
    >>> d["u"] = 2
    >>> d >>= lambda y: {"w": y**2}
    >>> d["v"] = 8
    >>> decolorize(str(d.history)) == '{j9_045f5ac950e6b2ff74f26c099994c606a119b: {Rs_92162dea64a7462725cac7dcee71b67669f69, uI_acddd31feb9259465f280b47ba1310d928122}, MOQ356EM3Aw3fpX8bh3lbZBjdhuGHJTLdHHU130o: None, dH_b1735f953d1c9a6859e61eaea2f6012e6193d: None}'
    True
    >>> d["d"] = d
    >>> d.show(colored=False)
    {
        "id": "il-YWAqTLqxXMPK7BGjEe1rQra32prLvrinN360M",
        "ids": {
            "w": "yFRT.QXWbEBxKPv6.HY0WTtTUxrGHJTLdHHU130o",
            "y": "Rs_92162dea64a7462725cac7dcee71b67669f69",
            "u": "uI_acddd31feb9259465f280b47ba1310d928122",
            "v": "dH_b1735f953d1c9a6859e61eaea2f6012e6193d",
            "d": "9SjmNApbfmSKqS051DRVOda9hlGGHJTLdHHU130o"
        },
        "w": "→(y)",
        "y": 7,
        "u": 2,
        "v": 8,
        "d": {
            "id": "BlZvumbNqO9tdyGB3f8wXY0GhGEGHJTLdHHU130o",
            "ids": {
                "w": "yFRT.QXWbEBxKPv6.HY0WTtTUxrGHJTLdHHU130o",
                "y": "Rs_92162dea64a7462725cac7dcee71b67669f69",
                "u": "uI_acddd31feb9259465f280b47ba1310d928122",
                "v": "dH_b1735f953d1c9a6859e61eaea2f6012e6193d"
            },
            "w": "→(y)",
            "y": 7,
            "u": 2,
            "v": 8
        }
    }
    >>> d["s"] = 1
    >>> del d["u"]
    >>> d["p"] = 82
    >>> d["q"] = 18
    >>> from ldict import decolorize
    >>> decolorize(str(d.history)) == '{yFRT.QXWbEBxKPv6.HY0WTtTUxrGHJTLdHHU130o: None, 38_19e4d550a16004128ea17f609178b75aea8a6: {dH_b1735f953d1c9a6859e61eaea2f6012e6193d, Rs_92162dea64a7462725cac7dcee71b67669f69}, 9SjmNApbfmSKqS051DRVOda9hlGGHJTLdHHU130o: None, wo_dbc5bf9d6d53cdc50c64e67323f8a3f8bb04d: {pt_369001ff096b860c63702a81e7bb7dc6252ae, Sr_028bb0aa9a6ddd4c6527ed7a94fd3322b9bfb, gv_06cc5343c944510b23dca462b64fe26acc2a2}}'
    True

    Parameters
    ----------
    d
    key

    Returns
    -------

    """
    lastitem = d.last and d.history[d.last]
    if d.last == hosh:
        del d.history[d.last]
        hist = list(d.history.keys())
        d.last = hist[-1] if len(hist) > 0 else None
    elif isinstance(lastitem, set) and hosh in lastitem:  # TODO: check inside list?
        lastitem.remove(hosh)
        del d.history[d.last]
        d.last /= hosh
        d.history[d.last] = lastitem if len(lastitem) > 1 else None  # pragma: no cover
    else:
        d.history = {}
        hosh = d.identity.h
        many = set()
        for k, v in d.hoshes.items():
            if v.etype == "ordered":
                if hosh != d.identity.h:
                    d.history[hosh] = None if len(many) == 1 else many
                    hosh = d.identity.h
                    many = set()
                d.history[v] = None
            else:
                hosh *= v
                many.add(v)
        if hosh != d.identity.h:
            d.history[hosh] = None if len(many) == 1 else many
        d.last = list(d.history.keys())[-1]
