import re
import os.path
import sys

from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_file_location

MAIN_MODULE_NAME = None
constant_assignment_pattern = re.compile(r"^([A-Z_][A-Z0-9_]*)\s*=\s*(.+)")
preamble = """import sys

def __my_setattr__(name, value, line_number):
    if name == name.upper() and name in sys.modules[__name__].__dict__:
        print(name + ", on line %s, is a constant; you cannot change its value." %
              line_number
             )
        return
    setattr(sys.modules[__name__], name, eval(value))

sys.modules[__name__].__setattr__ = __my_setattr__
"""


def transform_constant_assignment(source):
    """Identifies simple constant assignments and replace them by a
       special function call. Here, a constant is defined as any identifier
       written in uppercase letters.

       Note that this does not work if the value assigned is a tuple without
       enclosing parens, i.e.

       A = (1, 2)  # ok
       B = 1, 2  # not ok
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
    new_lines = preamble.split("\n")
    for line_number, line in enumerate(lines):
        match = re.search(constant_assignment_pattern, line)
        if match:
            new_lines.append(
                "sys.modules[__name__].__setattr__("
                + f"{repr(match.group(1))}, {repr(match.group(2))}, {line_number})"
            )
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


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
        # global MAIN_MODULE_NAME
        # if module.__name__ == MAIN_MODULE_NAME:
        #     module.__name__ = "__main__"
        #     MAIN_MODULE_NAME = None

        with open(self.filename) as f:
            source = f.read()

        source = transform_constant_assignment(source)
        exec(source, sys.modules[module.__name__].__dict__)


test_code = """
print('Testing')
a = 1
AB = 36
AB = 44
ABC = 1, 2, 4
ABC = 3, 3
print(a, 'should be 1')
print(AB, 'should be 36')
print(ABC, 'should be (1, 2, 4)')
"""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        MAIN_MODULE_NAME = sys.argv[-1]
        __import__(MAIN_MODULE_NAME)
    else:
        exec(transform_constant_assignment(test_code), {})
