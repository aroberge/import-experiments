""" Simple demo codec

This codec replaces any Python identifier (token) represented by the
single Greek letter 'λ' by the corresponding string 'lambda' which is
the Python keyword.

The source is assumed to be encoded in utf-8.
To help identify which parts are optional, we use USE_LAMBDA as a global
variable. Setting it to False, will default to using the normal utf-8 encoding.
"""

import codecs
import encodings
from tokenize import generate_tokens

from io import StringIO

utf8 = encodings.search_function("utf8")
USE_LAMBDA = True


class Token:
    """Token as generated from tokenize.generate_tokens written here in
       a more convenient form for our purpose.
    """

    def __init__(self, token):
        self.type = token[0]
        self.string = token[1]
        self.start_line, self.start_col = token[2]
        self.end_line, self.end_col = token[3]
        # ignore last parameter which is the logical line


def lambda_transform_string(text):
    """Simple transformation: replaces any single token λ by lambda.

        If we do not need to use a console/REPL, a simpler version of this
        function would be as follows:

        def lambda_transform_string(text):
            import tokenize
            tokens = []
            for tok_type, tok_string, _, _, _ in tokenize.generate_tokens(
                StringIO(text).readline
            ):
                if tok_string == "λ":
                    tok_string = "lambda"
                tokens.append((tok_type, tok_string))
            return tokenize.untokenize(tokens)

        H
    """
    result = []
    prev_col = 0
    prev_lineno = 0

    for tok in generate_tokens(StringIO(text).readline):
        token = Token(tok)
        if not token.string.strip(" \t"):  # we keep track of the spaces below
            continue

        if token.start_line > prev_lineno:
            prev_col = 0
        if token.start_col > prev_col and token.string != "\n":
            result.append(" " * (token.start_col - prev_col))
        prev_col = token.end_col
        prev_lineno = token.end_line

        if token.string == "λ":
            result.append("lambda")
        else:
            result.append(token.string)

    result = "".join(result)
    return result


def lambda_decode(input, errors="strict"):
    text, length = utf8.decode(input, errors)
    if USE_LAMBDA:
        text = lambda_transform_string(text)
    return text, length


class LambdaIncrementalDecoder(encodings.utf_8.IncrementalDecoder):
    def decode(self, input, final=False):
        self.buffer += input
        if final:
            buff = self.buffer
            self.buffer = b""
            if USE_LAMBDA:
                text, _ = lambda_decode(buff)
                buff = text.encode("utf-8")
            return super().decode(buff, final=True)
        else:
            return ""


def search_function(encoding):
    if encoding != "lambda-encoding":
        return None

    return codecs.CodecInfo(
        name="lambda-encoding",
        encode=utf8.encode,
        decode=lambda_decode,
        incrementalencoder=utf8.incrementalencoder,
        incrementaldecoder=LambdaIncrementalDecoder,
        streamreader=encodings.utf_8.StreamReader,
        streamwriter=utf8.streamwriter,
    )


codecs.register(search_function)
