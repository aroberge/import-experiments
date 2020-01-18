import test

test.XX = "a"  # should not change
test.a = 42
print(test.XX, test.a, ": should be 36 42")

A = 0
A = 2

try:
    A += 1
except TypeError:
    print("Augmented assignment cannot be done.")

a = 0
a += 1

print(A, a, "should be 0 1")
