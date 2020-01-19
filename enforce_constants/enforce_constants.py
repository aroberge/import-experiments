"""This is a simple proof of concept. It is not meant to be taken seriously."""

import os.path
import sys
# even though it is not needed here, we import typing so that
# it will not be processed by our import hook.
import typing  # noqa

from constant_module_type import ModuleWithConstants
from transformer import transform_assignment

from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_file_location

Main_Module_Name = None


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
        """Import the source code, transform it before executing it so that
           it is known to Python."""
        global Main_Module_Name
        module.__class__ = ModuleWithConstants

        with open(self.filename) as f:
            source = f.read()

        if Main_Module_Name is not None:
            sys.modules["__main__"] = sys.modules[module.__name__]
            module.__name__ = "__main__"
            Main_Module_Name = None

        source = transform_assignment(source)
        exec(source, sys.modules[module.__name__].__dict__)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        Main_Module_Name = sys.argv[-1]
        print("__main__ is", Main_Module_Name)
        __import__(Main_Module_Name)
        sys.modules["enforce_constants"] = sys.modules["__main__"]
        __name__ = "enforce_constants"
