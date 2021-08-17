from dataclasses import dataclass


@dataclass
class Empty:
    version: str

    def __rshift__(self, other):
        """
        Usage:

        >>> from ldict import ø
        >>> d = ø >> {"x": 2}
        >>> d.show(colored=False)
        {
            "id": "00000000000dc-DMDXCtigJFu0bLt-KK",
            "ids": {
                "x": "00000000000dc-DMDXCtigJFu0bLt-KK"
            },
            "x": 2
        }
        >>> from ldict import Ø
        >>> d = Ø >> {"x": 2}
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
        return Ldict(other, version=self.version)
