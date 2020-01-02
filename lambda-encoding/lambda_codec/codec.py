# See https://docs.python.org/dev/library/codecs.html

# encode: str -> bytes
# decode: bytes -> str

import codecs
import encodings
import tokenize

from io import StringIO

USE_LAMBDA = True


def lambda_transform_string(text):
    tokens = []
    for tok_type, tok_string, _, _, _ in tokenize.generate_tokens(
        StringIO(text).readline
    ):
        if tok_string == "λ":
            tok_string = "lambda"
        tokens.append((tok_type, tok_string))

    return tokenize.untokenize(tokens)


def lambda_decode(input, errors="strict"):
    utf8 = encodings.search_function("utf8")
    text, _ = utf8.decode(input, errors)
    if USE_LAMBDA:
        text = lambda_transform_string(text)
    return text, len(text)


class LambdaIncrementalDecoder(encodings.utf_8.IncrementalDecoder):

    def decode(self, input, final=False):
        self.buffer += input
        if final:
            buff = self.buffer
            self.buffer = b''
            if USE_LAMBDA:
                text, length = lambda_decode(buff)
                buff = text.encode("utf-8")
            return super().decode(buff, final=True)
        else:
            return ''


def search_function(encoding):
    if encoding != "lambda-encoding":
        return None
    # Assume utf8 encoding
    utf8 = encodings.search_function("utf8")

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
