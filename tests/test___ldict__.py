from unittest import TestCase

from ldict import ldict


class TestLdict(TestCase):
    def test_setitem(self):
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

        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d["z"] = lambda x, y: x * y
        self.assertEqual(
            """{
    "id": "qhB7bRuqe3Xx4WUXoM8MLlP2gE97svU1eMgT8-4CjpO-XbTS3maOpbQUqdxA8IbK",
    "ids": "<2 hidden ids>",
    "x": 3,
    "y": 5,
    "z": "<unevaluated lazy field>"
}""",
            str(d),
        )

        self.assertEqual(d.z, 15)

    def test_rshift(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d >>= lambda x, y: {"z": x * y}
        self.assertEqual(
            """{
    "id": "2mgMtxYKDMigDpFqn.NVXmhemFJIWSpBb4Tj4H6w3eLpVC6xMxdI3Z1NLADgSrRX",
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
