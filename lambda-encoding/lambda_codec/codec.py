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
import tokenize

from io import StringIO

utf8 = encodings.search_function("utf8")
USE_LAMBDA = True


def lambda_transform_string(text):
    """Simple transformation: replaces any single token λ by lambda"""
    tokens = []
    for tok_type, tok_string, _, _, _ in tokenize.generate_tokens(
        StringIO(text).readline
    ):
        if tok_string == "λ":
            tok_string = "lambda"
        tokens.append((tok_type, tok_string))
    return tokenize.untokenize(tokens)


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
