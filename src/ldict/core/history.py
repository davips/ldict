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
from ldict.config import GLOBAL


def extend_history(history, last, hosh):
    """
    >>> from ldict import ldict, setup
    >>> setup(history=True)  # Keep history of ids of all applied functions.
    >>> d = ldict()
    >>> d.history
    {}
    >>> d["x"] = 5
    >>> from ldict import decolorize
    >>> from garoupa import ø40
    >>> d.history == {ø40*".T_f0bb8da3062cc75365ae0446044f7b3270977": None}
    True
    >>> d["y"] = 7
    >>> d.history == {ø40*"mP_2d615fd34f97ac906e162c6fc6aedadc4d140": {ø40*"mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8", ø40*".T_f0bb8da3062cc75365ae0446044f7b3270977"}}
    True

    Parameters
    ----------
    history
    last
    hosh

    Returns
    -------

    """
    if not GLOBAL["history"]:
        return last
    if not history or hosh.etype == "ordered" or last and "_" not in last.id[:3]:
        last = hosh
        history[last] = None
    else:
        many = history.pop(last)
        previous_last = last
        last *= hosh
        if many is None:
            history[last] = {previous_last, hosh}
        else:
            many.add(hosh)
            history[last] = many
    return last


def rewrite_history(history, last, hosh, hoshes):
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
    >>> from garoupa import ø40
    >>> d.history == {ø40*"mP_2d615fd34f97ac906e162c6fc6aedadc4d140": {ø40*"mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8", ø40*".T_f0bb8da3062cc75365ae0446044f7b3270977"}}
    True
    >>> d["z"] = 8
    >>> d.history == {ø40*"td_36054eee402a39b19bc9c3162df3424f8ec1f": {ø40*"7q_3c95f44b01eb0f9e2da3bda1665567bc21bde", ø40*"mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8", ø40*".T_f0bb8da3062cc75365ae0446044f7b3270977"}}
    True
    >>> list(d.ids.keys()) == ["x", "y", "z"]
    True
    >>> del d["x"]
    >>> list(d.ids.keys()) == ["y", "z"]
    True
    >>> del d["z"]
    >>> d.history == {ø40*"mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8": None}
    True
    >>> d >>= lambda y: {"x": y**2}
    >>> d >>= lambda y: {"w": y**2}
    >>> del d["x"]
    >>> del d["w"]
    >>> d.history == {ø40*"mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8": None}
    True
    >>> d["u"] = 2
    >>> d >>= lambda y: {"w": y**2}
    >>> d["v"] = 8
    >>> d.history == {
    ...     ø40*"Hb_7314dcc8edea97e1ca271ebd99e9a7027e41e": {
    ...         ø40*"lg_3e7c0b98a45ac2a4c1bfe594d68a486791c45",
    ...         ø40*"mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8"
    ...     },
    ...     ø40*"J-GKFUnorPV20E7RfczBXKCxn9AGHJTLdHHU130o": None,
    ...     ø40*"3q_94bb5942b4b0899e2da30eb1665567ac21bde": None
    ... }
    True
    >>> d["d"] = d
    >>> d.show(colored=False)
    {
        "id": "n8SY5Tc6e3h6lMvKYXZiGStDD622prLvrinN360M",
        "ids": {
            "w": "Jba-cVOujao7LA9-RhV6riospexGHJTLdHHU130o",
            "y": "mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8",
            "u": "lg_3e7c0b98a45ac2a4c1bfe594d68a486791c45",
            "v": "3q_94bb5942b4b0899e2da30eb1665567ac21bde",
            "d": "lnQdLh5SnHAqOWlLOVRsogxTllsGHJTLdHHU130o"
        },
        "w": "→(y)",
        "y": 7,
        "u": 2,
        "v": 8,
        "d": {
            "id": "LrKo5MNkOCR8B-lYRx835WnomGGGHJTLdHHU130o",
            "ids": {
                "w": "Jba-cVOujao7LA9-RhV6riospexGHJTLdHHU130o",
                "y": "mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8",
                "u": "lg_3e7c0b98a45ac2a4c1bfe594d68a486791c45",
                "v": "3q_94bb5942b4b0899e2da30eb1665567ac21bde"
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
    >>> from garoupa import ø40
    >>> d.history == {
    ...     ø40*"Jba-cVOujao7LA9-RhV6riospexGHJTLdHHU130o": None,
    ...     ø40*"ql_d9432b72fd415edb262b26ea29b4c6470e3a7": {
    ...         ø40*"3q_94bb5942b4b0899e2da30eb1665567ac21bde",
    ...         ø40*"mX_dc5a686049ceb1caf8778e34d26f5fd4cc8c8"
    ...     },
    ...     ø40*"lnQdLh5SnHAqOWlLOVRsogxTllsGHJTLdHHU130o": None,
    ...     ø40*"J1_ed3b1fb24ac128f66047a99c71b36a016a962": {
    ...         ø40*"oY_0275e7afca5c1a73e43c6e7c4777abdeadb9f",
    ...         ø40*"zF_90477513efef849fb70166c137f54f6039f7e",
    ...         ø40*"Mr_27c70f609f2c33eeb30ab18413467f3653e44"
    ...     }
    ... }
    True

    Parameters
    ----------
    d
    key

    Returns
    -------

    """
    if not GLOBAL["history"]:
        return last
    lastitem = last and history[last]
    if last == hosh:
        del history[last]
        hist = list(history.keys())
        last = hist[-1] if len(hist) > 0 else None
    elif isinstance(lastitem, set) and hosh in lastitem:  # TODO: check inside list?
        lastitem.remove(hosh)
        del history[last]
        last /= hosh
        history[last] = lastitem if len(lastitem) > 1 else None  # pragma: no cover
    else:
        history.clear()
        hosh = hosh.ø
        many = set()
        for k, v in hoshes.items():
            if v.etype == "ordered":
                if hosh != hosh.ø:
                    history[hosh] = None if len(many) == 1 else many
                    hosh = hosh.ø
                    many = set()
                history[v] = None
            else:
                hosh *= v
                many.add(v)
        if hosh != hosh.ø:
            history[hosh] = None if len(many) == 1 else many
        last = list(history.keys())[-1]
    return last
