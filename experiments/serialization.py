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
import pickle
from timeit import timeit

import lz4.frame as lz4
from pandas import DataFrame
from scipy.io.arff import loadarff

# from ldict.compression import pack
# from garoupa import ø
# ar = loadarff("airlines50k.arff")
# print(ø * pack(DataFrame(ar)))
# ar = loadarff("airlines50k.arff")
# print(ø * pack(DataFrame(ar)))
# ar = loadarff("airlines50k.arff")
# print(ø * pack(DataFrame(ar)))
# exit()

for file in ["airlines50k.arff"]:  # , "airlines100k.arff"]:
    print()
    print(file)


    def arff():
        return loadarff(file)


    def df(ar):
        return DataFrame(ar)


    def pick(df):
        return pickle.dumps(df)


    def comp(pi):
        return lz4.compress(pi)


    def decomp(co):
        return lz4.decompress(co)


    def unpick(de):
        return pickle.loads(de)


    print("load arff", timeit(arff, number=1), sep="\t")
    x = arff()
    print("convert to pandas", timeit(lambda: df(x), number=1), sep="\t")
    x = df(x)
    print("pickle", timeit(lambda: pick(x), number=1), sep="\t")
    x = pick(x)
    print("pickle size:", len(x))
    print("compress lz4", timeit(lambda: comp(x), number=1), sep="\t")
    x = comp(x)
    print("final size:", len(x))
    print("uncompress lz4", timeit(lambda: decomp(x), number=1), sep="\t")
    x = decomp(x)
    print("unpickle", timeit(lambda: unpick(x), number=1), sep="\t")
    x = unpick(x)

"""
airlines100k
18.11314875399694
1.996661891695112
0.48285040399059653
0.28235141932964325
"""

"""
airlines200k
36.43428422510624
3.4813605742529035
0.9991299170069396
0.7922783433459699
"""
