import test
print("This is test_b.py")

A = 42
print("A = ", A)

A = 32

A += 1  # this is not prevented to happen

print("I cheated: A = ", A)
