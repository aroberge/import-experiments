"""
main.py
----------


"""
import argparse
import os
import runpy
import sys

from . import console

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Description",
)
parser.add_argument(
    "source",
    nargs="?",
    help="""Name of the script to be run as though it was the main module
    run by Python, so that __name__ does equal '__main__'.
    """,
)


def main():
    console_dict = {"exit": lambda: os._exit(1)}  # force clean exit from console
    args = parser.parse_args()

    if args.source is not None:
        if sys.flags.interactive:
            source = args.source
            if source.endswith(".py"):
                source = source[:-3]
            module_dict = runpy.run_module(source, run_name="__main__")
            console_dict.update(module_dict)
            console.start_console(local_vars=console_dict)
        else:
            runpy.run_path(args.source, run_name="__main__")
    else:
        console.start_console(local_vars=console_dict)


main()
