import code
import tokenize

from . import codec


def my_input(prompt):
    text = input(prompt)
    try:
        result = codec.lambda_transform_string(text)
    except tokenize.TokenError as e:
        print("TokenError: " + str(e))
        result = ""
    return result


def start_console(local_vars=None):
    code.interact(banner="λ console", readfunc=my_input, local=local_vars)
