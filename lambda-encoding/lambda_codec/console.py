import code

from . import codec


def my_input(prompt):
    text = input(prompt)
    return codec.lambda_transform_string(text)


def start_console():
    code.interact(banner="λ console", readfunc=my_input)
