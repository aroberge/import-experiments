import test

test.XX = "new value"  # should not change
assert test.XX == 36

test.const = "'changing final constant from module test_b'"
assert test.const == 1

test.a = 42  # not a constant
assert test.a == 42

A = 0
A = 2

assert A == 0
A += 1  # cheating
assert A == 1
