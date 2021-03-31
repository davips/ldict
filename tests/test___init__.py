from unittest import TestCase

from garoupa.hash import identity

from ldict import ldict, OverwriteException


class TestLdict(TestCase):
    def test_setitem(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 4
        d["z"] = 5
        self.assertEqual("""{
    "id": "Wrhfg9ke6xjtHhwJKYw1ezsmV6PBsufXnYYdWxed2ZM",
    "x": 3,
    "y": 4,
    "z": 5,
    "id_*": "<3 hidden fields>"
}""", str(d))

        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d["z"] = (lambda x, y: x * y)
        self.assertEqual("""{
    "id": "iIb1fuhlZJ8XjL3sT3T2fGdYBVsqnHOoZDx80jly9zX",
    "x": 3,
    "y": 5,
    "z": "<unevaluated lazy field>",
    "id_*": "<3 hidden fields>"
}""", str(d))

        self.assertEqual(d.z, 15)

    def test_rshift(self):
        d = ldict()
        d["x"] = 3
        d["y"] = 5
        d >> (lambda x, y: {"z": x * y})
        self.assertEqual("""{
    "id": "7dZknVz8pKQsKfAyn2MRE2oK35klAWI5Q9iKKeb2fpe",
    "x": 3,
    "y": 5,
    "z": "<unevaluated lazy field>",
    "id_*": "<3 hidden fields>"
}""", str(d))

        self.assertEqual(d.z, 15)

    def test_overwrite(self):
        a = ldict(x=3)

        def f():
            a['x'] = 5

        self.assertRaises(OverwriteException, f)

        l = lambda x, y: {"x": x * y}
        l.hash = identity

        def g():
            a >> l

        self.assertRaises(OverwriteException, g)
