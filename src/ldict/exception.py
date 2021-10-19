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
import importlib


def check_access(id, readonly, key):
    if readonly:  # pragma: no cover
        raise ReadOnlyLdict(f"Cannot change a readonly ldict ({id}).", key)
    if not isinstance(key, str):
        raise WrongKeyType(f"Key must be string, not {type(key)}.", key)


def check_package(module_name, obj=None):
    if obj is not None and not obj.__class__.__module__.startswith(module_name):
        return None
    try:
        return importlib.import_module(module_name)
    except ImportError:
        package = module_name.split(".")[0]
        raise MissingLibraryDependence(
            f"Package {package} should be installed to be able to handle objects of type {type(obj)}."
        )


class OverwriteException(Exception):
    pass


class DependenceException(Exception):
    pass


class NoInputException(Exception):
    pass


class FunctionETypeException(Exception):
    pass


class FromØException(Exception):
    pass


class MissingField(Exception):
    pass


class NoReturnException(Exception):
    pass


class BadOutput(Exception):
    pass


class WrongKeyType(Exception):
    pass


class WrongValueType(Exception):
    pass


class ConflictingParameter(Exception):
    pass


class InconsistentLange(Exception):
    pass


class EmptyNextToGlobalCache(Exception):
    pass


class MultipleIdsForFunction(Exception):
    pass


class MissingIds(Exception):
    pass


class WrongId(Exception):
    pass


class MissingLibraryDependence(Exception):
    pass


class DTypeCannotBeObject(Exception):
    pass


class UnderscoreInField(Exception):
    pass


class MultipleDicts(Exception):
    pass


class UndefinedSeed(Exception):
    pass


class ReadOnlyLdict(Exception):
    pass
