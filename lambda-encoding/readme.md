# λ-encoding

This is an experiment to create a custom encoding where the Greek letter
λ would be interpreted/converted as the Python lambda keyword.
The purpose is to learn what is needed to create a custom encoding,
and making it available for all programs without implicitly importing it.

My original motivation for looking at codecs was from
[a comment left on one of my blog posts](https://aroberge.blogspot.com/2015/10/from-experimental-import-somethingnew.html?showComment=1444820092247#c5491554166542490140)
some four years ago.
At some point, I stumbled upon Dropbox's [Pyxl package](https://github.com/dropbox/pyxl).
I used GvRs' Python 3 version, [Pyxl 3](https://github.com/gvanrossum/pyxl3),
as a starting guide for this much simpler project.

## How to use

Either on the first or second line of your Python script, insert a line like

    # coding: lambda-encoding

I would have prefered to use

    # coding: λ-encoding

but, alas, the name of the encoding has to use only ascii characters.

A sample program, `test.py`, is included for convenience.
You can then run that program or your own following one of the methods described below.

### Environment variable

We assume you are in the same directory where this file and the
file `usercustomize.py` are located.  You can set the environment variable
PYTHONPATH to be equal to this directory. On Windows, this can be done by

    set PYTHONPATH=%CD%

Doing so will ensure that Python will executes `usercustomize.py` prior
to executing any user code. The file `usercustomize.py` does the
require import to ensure that the lambda-encoding codec is registered.
