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

import json
import re

from ldict.customjson import CustomJSONEncoder
from ldict.lazy import islazy


def decolorize(txt):
    """
    >>> decolorize("\x1b[38;5;116m\x1b[1m\x1b[48;5;0mB\x1b[0m\x1b[38;5;85m\x1b[1m\x1b[48;5;0ma\x1b[0m\x1b[38;5;157m\x1b[1m\x1b[48;5;0m_\x1b[0m\x1b[38;5;122m\x1b[1m\x1b[48;5;0m3\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0md\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0mc\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;84m\x1b[1m\x1b[48;5;0ma\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0ma\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0m4\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m5\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;85m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;157m\x1b[1m\x1b[48;5;0m4\x1b[0m\x1b[38;5;122m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m2\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m1\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m6\x1b[0m\x1b[38;5;84m\x1b[1m\x1b[48;5;0m0\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0mb\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0m9\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0m5\x1b[0m\x1b[38;5;116m\x1b[1m\x1b[48;5;0m7\x1b[0m\x1b[38;5;85m\x1b[1m\x1b[48;5;0m4\x1b[0m\x1b[38;5;157m\x1b[1m\x1b[48;5;0m2\x1b[0m\x1b[38;5;122m\x1b[1m\x1b[48;5;0me\x1b[0m\x1b[38;5;86m\x1b[1m\x1b[48;5;0me\x1b[0m\x1b[38;5;156m\x1b[1m\x1b[48;5;0mc\x1b[0m\x1b[38;5;114m\x1b[1m\x1b[48;5;0m2\x1b[0m\x1b[38;5;80m\x1b[1m\x1b[48;5;0mb\x1b[0m")
    'Ba_31d001c1aa4056b46b2016160bb95742eec2b'

    Parameters
    ----------
    txt

    Returns
    -------

    """
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", txt)


def ldict2txt(d, all):
    """
    Textual representation of a ldict object

    >>> from ldict import ldict
    >>> d = ldict(x=1,y=2)
    >>> decolorize(ldict2txt(d, False))
    '{\\n    "id": "Tb_334cc16924a8bdc38205599e516203f9054c4",\\n    "ids": "<2 hidden ids>",\\n    "x": 1,\\n    "y": 2\\n}'
    >>> decolorize(ldict2txt(d, True))
    '{\\n    "id": "Tb_334cc16924a8bdc38205599e516203f9054c4",\\n    "ids": {\\n        "x": "lv_56eec09cd869410b23dcb462b64fe26acc2a2",\\n        "y": "yI_a331070d4bcdde465f28ba37ba1310e928122"\\n    },\\n    "x": 1,\\n    "y": 2\\n}'

    Parameters
    ----------
    d
    all

    Returns
    -------

    """
    dic = ldict2dic(d,all)
    txt = json.dumps(dic, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)
    for k, v in dic.items():
        if k == "id":
            txt = txt.replace(dic[k], d.hosh.idc)
    if all:
        for k, v in d.hoshes.items():
            txt = txt.replace(v.id, v.idc)  # REMINDER: workaround to avoid json messing with colors
    return txt


def ldict2dic(d, all):
    from ldict.lazy import Lazy
    from ldict.ldict_ import ldict
    dic = d.data.copy()
    for k, v in d.data.items():
        if islazy(v):
            dic[k] = str(v)
        elif isinstance(v, ldict):
            dic[k] = ldict2dic(v, all)
        if not all:
            dic["ids"] = "<1 hidden id>" if len(dic["ids"]) == 1 else f"<{len(d) -  2} hidden ids>"
    return dic
