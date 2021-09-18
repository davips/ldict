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
from json import loads

from orjson import dumps, OPT_SORT_KEYS, OPT_SERIALIZE_NUMPY

from ldict.exception import check_package


def default_orjson_encoder(obj):
    r"""
    >>> import numpy as np
    >>> default_orjson_encoder(np.array([[1/3,5/4],[1.3**64, -1]]))
    {'_type': "<class 'numpy.ndarray'>", 'repr': 'str', 'dtype': 'float64', 'obj': '[[0.3333333333333333,1.25],[19605347.64307615,-1.0]]'}
    """
    if m := check_package("pandas.core", obj):
        if isinstance(obj, (m.frame.DataFrame, m.series.Series)):
            dic = obj.to_dict()
            dic["_type"] = str(type(obj))
            return dic
    elif m := check_package("numpy", obj):
        if isinstance(obj, m.ndarray):
            try:
                dump = dumps(obj, option=OPT_SORT_KEYS | OPT_SERIALIZE_NUMPY)
                obj2, repr = dump.decode(encoding="utf8"), "str"
            except TypeError:
                obj2, repr = obj.tolist(), "list"
            return {"_type": str(type(obj)), "repr": repr, "dtype": str(obj.dtype), "obj": obj2}
    raise TypeError  # pragma: no cover


def encode(obj):
    r"""
    >>> import pandas as pd
    >>> df = pd.DataFrame(
    ...     [[1/3, 5/4], [1.3**54, "text"]],
    ...     index=["row 1", "row 2"],
    ...     columns=["col 1", "col 2"],
    ... )
    >>> df
                  col 1 col 2
    row 1  3.333333e-01  1.25
    row 2  1.422136e+06  text
    >>> encode(df)
    b'{"_type":"<class \'pandas.core.frame.DataFrame\'>","col 1":{"row 1":0.3333333333333333,"row 2":1422135.6537506874},"col 2":{"row 1":1.25,"row 2":"text"}}'
    >>> s = pd.Series(
    ...     [1/3, 5/4, (1.3)**54, "text"],
    ...     index=["row 1", "row 2", "row 3", "row 4"],
    ... )
    >>> s
    row 1          0.333333
    row 2              1.25
    row 3    1422135.653751
    row 4              text
    dtype: object
    >>> encode(s)
    b'{"_type":"<class \'pandas.core.series.Series\'>","row 1":0.3333333333333333,"row 2":1.25,"row 3":1422135.6537506874,"row 4":"text"}'
    >>> import numpy as np
    >>> encode(np.array([[1/3,5/4],[1.3**64, "text"]]))
    b'{"_type":"<class \'numpy.ndarray\'>","dtype":"<U32","obj":[["0.3333333333333333","1.25"],["19605347.64307615","text"]],"repr":"list"}'
    """
    return dumps(obj, default=default_orjson_encoder, option=OPT_SORT_KEYS)


def json_object_hook_decoder(dic):
    if '_type' in dic:
        if "pandas" in (typ := dic.pop("_type")):
            m = check_package("pandas.core")
            if "DataFrame" in typ:
                return m.frame.DataFrame.from_dict(dic)
            elif "Series" in typ:
                return m.series.Series(data=dic.values(), index=dic.keys())
        if "ndarray" in typ and "numpy" in typ:
            m = check_package("numpy")
            obj = loads(dic["obj"]) if dic["repr"] == "str" else dic["obj"]
            return m.array(obj, dtype=dic["dtype"])
    return dic


def decode(blob):
    r"""
    >>> df = b'{"_type":"<class \'pandas.core.frame.DataFrame\'>","col 1":{"row 1":0.3333333333333333,"row 2":1422135.6537506874},"col 2":{"row 1":1.25,"row 2":"text"}}'
    >>> decode(df)
                  col 1 col 2
    row 1  3.333333e-01  1.25
    row 2  1.422136e+06  text
    >>> s = b'{"_type":"<class \'pandas.core.series.Series\'>","row 1":0.3333333333333333,"row 2":1.25,"row 3":1422135.6537506874,"row 4":"text"}'
    >>> decode(s)
    row 1          0.333333
    row 2              1.25
    row 3    1422135.653751
    row 4              text
    dtype: object
    >>> n = {'_type': "<class 'numpy.ndarray'>", 'repr': 'str', 'dtype': 'float64', 'obj': '[[0.3333333333333333,1.25],[19605347.64307615,-1.0]]'}
    >>> decode(encode(n))
    array([[ 3.33333333e-01,  1.25000000e+00],
           [ 1.96053476e+07, -1.00000000e+00]])
    """
    return loads(blob, object_hook=json_object_hook_decoder)
