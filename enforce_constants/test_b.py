import test

test.XX = "a"  # should not change
test.a = 42
print(test.XX, test.a, ": should be 36 42")

A = 42
print("A = ", A)
A = 32

A += 1  # this is not prevented to happen

print("I cheated: A = ", A)
