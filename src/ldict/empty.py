class Empty:
    def __rshift__(self, other):
        """
        Usage:

        >>> from ldict import ø
        >>> d = ø >> {"x": 2}
        >>> d.show(colored=False)
        {
            "id": "000000000000000000000c3aop1df5AZXCRMY3yInQeUYccGQRclWo8TvfKPB4YT",
            "ids": {
                "x": "000000000000000000000c3aop1df5AZXCRMY3yInQeUYccGQRclWo8TvfKPB4YT"
            },
            "x": 2
        }
        """
        from ldict import Ldict
        return Ldict(other)
