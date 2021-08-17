# #  Copyright (c) 2021. Davi Pereira dos Santos
# #  This file is part of the ldict project.
# #  Please respect the license - more about this in the section (*) below.
# #
# #  ldict is free software: you can redistribute it and/or modify
# #  it under the terms of the GNU General Public License as published by
# #  the Free Software Foundation, either version 3 of the License, or
# #  (at your option) any later version.
# #
# #  ldict is distributed in the hope that it will be useful,
# #  but WITHOUT ANY WARRANTY; without even the implied warranty of
# #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #  GNU General Public License for more details.
# #
# #  You should have received a copy of the GNU General Public License
# #  along with ldict.  If not, see <http://www.gnu.org/licenses/>.
# #
# #  (*) Removing authorship by any means, e.g. by distribution of derived
# #  works or verbatim, obfuscated, compiled or rewritten versions of any
# #  part of this work is a crime and is unethical regarding the effort and
# #  time spent here.
# #
# from dataclasses import dataclass
#
# from garoupa import Hosh
#
#
# @dataclass
# class Cache:
#     fields: list
#     identity: Hosh
#
#     def __post_init__(self):
#         self.input_fields = self.fields
#         self.output_fields = self.fields
#         self.hosh = self.identity
#
#     def __call__(self, **kwargs):
#         # print(1111111111111111)
