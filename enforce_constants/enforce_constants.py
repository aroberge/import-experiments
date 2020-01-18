"""This is a simple proof of concept. It is not meant to be taken seriously."""

import os.path
import re
import sys
import types
import typing  # noqa

from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_file_location

MAIN_MODULE_NAME = None
assignment_pattern = re.compile(r"^\s*([\w][\w\d]*)\s*=\s*(.+)")
final_declaration_pattern = re.compile(r"^([\w][\w\d]*)\s*:\s*Final\s*=\s*(.+)")


def transform_constant_assignment(source, mod_name):
    """Identifies simple constant assignments and replace them by a
       special function call. Here, a constant is defined as any identifier
       written in uppercase letters.
    """
    global MAIN_MODULE_NAME
    # First, ensure that if the module is meant to be run as main script,
    # anything like
    #     if __name__ == '__main__'
    # would still work
    if MAIN_MODULE_NAME is not None:
        if "'__main__'" in source:
            source = source.replace("'__main__'", f"'{MAIN_MODULE_NAME}'")
        elif '"__main__"' in source:
            source = source.replace('"__main__"', f'"{MAIN_MODULE_NAME}"')
        MAIN_MODULE_NAME = None

    lines = source.split("\n")
    new_lines = ["import sys"]
    for line_number, line in enumerate(lines):
        match = re.search(assignment_pattern, line)
        match_final = re.search(final_declaration_pattern, line)
        if match:
            name = match.group(1)
            indent = len(line) - len(line.lstrip())
            value = match.group(2)
            new_lines.append(
                " " * indent
                + "sys.modules[__name__].__setattr__("
                + f"{repr(name)}, ({value}))"
            )
        elif match_final:
            name = match_final.group(1)
            value = match_final.group(2)
            new_lines.append(
                "sys.modules[__name__].__setattr__("
                + f"{repr(name)}, ({value}), final=True)"
            )
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


class ModuleWithConstants(types.ModuleType):
    def __setattr__(self, attr, value, final=False):
        if not hasattr(self, "_constants_dict"):
            super().__setattr__("_constants_dict", {})
        if attr in self._constants_dict and not final:
            print(
                "You cannot change the value of %s.%s to %s"
                % (self.__name__, attr, value)
            )
        else:
            if final or attr == attr.upper():
                self._constants_dict[attr] = value
            super().__setattr__(attr, value)


class MyMetaFinder(MetaPathFinder):
    """A custom finder to locate modules.  The main reason for this code
       is to ensure that our custom loader, which does the code transformations,
       is used."""

    def find_spec(self, fullname, path, target=None):
        """finds the appropriate properties (spec) of a module, and sets
           its loader."""
        if not path:
            path = [os.getcwd()]
        if "." in fullname:
            name = fullname.split(".")[-1]
        else:
            name = fullname
        for entry in path:
            if os.path.isdir(os.path.join(entry, name)):
                # this module has child modules
                filename = os.path.join(entry, name, "__init__.py")
                submodule_locations = [os.path.join(entry, name)]
            else:
                filename = os.path.join(entry, name + ".py")
                submodule_locations = None
            if not os.path.exists(filename):
                continue

            return spec_from_file_location(
                fullname,
                filename,
                loader=MyLoader(filename),
                submodule_search_locations=submodule_locations,
            )
        return None  # we don't know how to import this


sys.meta_path.insert(0, MyMetaFinder())


class MyLoader(Loader):
    """A custom loader which will transform the source prior to its execution"""

    def __init__(self, filename):
        self.filename = filename

    def create_module(self, spec):
        return None  # use default module creation semantics

    def exec_module(self, module):
        """import the source code, transform it before executing it so that
           it is known to Python."""

        module.__class__ = ModuleWithConstants

        with open(self.filename) as f:
            source = f.read()

        source = transform_constant_assignment(source, module.__name__)
        exec(source, sys.modules[module.__name__].__dict__)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        MAIN_MODULE_NAME = sys.argv[-1]
        __import__(MAIN_MODULE_NAME)
