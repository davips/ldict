from unittest import TestCase

import pytest

from ldict import ldict, ø
from ldict_modules.empty import FromØException
from ldict import DependenceException, NoInputException


class TestLdict(TestCase):
    def test_setitem_vakue(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 4
        d["z"] = 5
        self.assertEqual(
            """{
    "id": "0000000000000000000009V1LaGXErf0c8MnOfiLiBgCV9NvR9xe68KJk4bZZp0C",
    "ids": "<2 hidden ids>",
    "x": 3,
    "y": 4,
    "z": 5
}""",
            str(d),
        )

    def test_setitem_function(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d["z"] = lambda x, y: x * y
        self.assertEqual(
            """{
    "id": "lP5q-u4W-2MVBg19Rgx42NxlhDsgLM30dqLJLMA28VKWt9I.jql945hVjwqxfcrQ",
    "ids": "<2 hidden ids>",
    "x": 3,
    "y": 5,
    "z": "<unevaluated lazy field>"
}""",
            str(d),
        )
        self.assertEqual(d.z, 15)

    def test_setitem_overwrite_value(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d["z"] = lambda x, y: x * y
        # Overwrite same value.
        d["y"] = 5
        self.assertEqual("lP5q-u4W-2MVBg19Rgx42OdRxcuXRNhux63n-bRszVIB3GacFTH4K5dvBCNx2gfm", d.id)
        # Repeate same overwrite.
        d["y"] = 5
        self.assertEqual("lP5q-u4W-2MVBg19Rgx42OdRxcuXRNhux63n-bRszVIB3GacFTH4K5dvBCNx2gfm", d.id)
        # Overwrite other value.
        d["y"] = 6
        self.assertEqual("lP5q-u4W-2MVBg19Rgx42LVk0W.Fvld.WQTI8KWS3aqpHT6ZMjsUhsF2KsyV3qyx", d.id)

    def test_setitem_overwrite_function(self):
        d = ldict()
        d["x"] = 1
        d["y"] = 2
        d["z"] = 3
        d["z"] = lambda x, y, z: x + y * z
        # Reapply same function.
        d["z"] = lambda x, y, z: x + y * z
        # Reapply same function.
        d["z"] = lambda x, y, z: x + y * z
        # self.assertEqual("qhB7bRuqe3Xx4WUXoM8MLcUxAMVp9-HCAK1o.meENYOjT.pGD4XI7dcRwd8E7f75", d.id)

    def test_rshift(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d >>= lambda x, y: {"z": x * y}
        self.assertEqual(
            """{
    "id": "1VP6w4Zv2WQfNmVGjoVzIiCDBS8mAsRBeFkDJysDvEYB.SHnnXTfP7JQXB6ccL0g",
    "ids": "<2 hidden ids>",
    "z": "<unevaluated lazy field>",
    "x": 3,
    "y": 5
}""",
            str(d),
        )

        self.assertEqual(d.z, 15)

    def test_overwrite(self):
        a = ldict(x=3)
        # a.show()
        # (a >> {"x": 3}).show()
        # self.assertEqual(a.idc, (a >> {"x": 3}).idc)  # overwrite
        b = ldict(y=4, x=3)
        self.assertEqual(b.idc, (a >> {"y": 4}).idc)  # new value
        # self.assertNotEqual(a, a >> {"x": 3})
        # def f():
        #     a["x"] = 5

    def test_illdefined_function(self):
        with pytest.raises(FromØException):
            ø >> (lambda y: {"x": 5})
        with pytest.raises(DependenceException):
            ø >> {"x": 5} >> (lambda y: {"x": 5})
        with pytest.raises(NoInputException):
            ø >> {"x": 5} >> (lambda: {"x": 5})


"""
        >>> d >>= {"y": 2}
        >>> d.show(colored=False)
        {
            "id": "0000000000000000000005ZAUVMzxwjwXbh7mLzet1L.rDnoCfw4gnGNFOvMzRW-",
            "ids": {
                "x": "000000000000000000000c3aop1df5AZXCRMY3yInQeUYccGQRclWo8TvfKPB4YT",
                "y": "0000000000000000000009WqwwLmiqGS.ArmqI0ypCV6vraJNpxBjfxWayMZI.iZ"
            },
            "x": 2,
            "y": 2
        }
        >>> d >>= (lambda x: {"x": x**2})
        >>> d.show(colored=False)
        {
            "id": "aMxJyzaP3pwUZmywZdR2Aal7WMRcOcoR6oAgBnvJcJ0j9sHBGGtBMV8XQNcx8vTQ",
            "ids": {
                "x": "000000000000000000000c3aop1df5AZXCRMY3yInQeUYccGQRclWo8TvfKPB4YT",
                "y": "0000000000000000000009WqwwLmiqGS.ArmqI0ypCV6vraJNpxBjfxWayMZI.iZ"
            },
            "x": 2,
            "y": 2
        }
"""

#         d = ldict(x=123123, y=88)
# d.show()
# e = d >> (lambda x, y: {"z": x ** 22, "w": x / y})


# TODO:
#   exception if function is not in G\H
#   all requirements from paper
