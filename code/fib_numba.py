from numba import jit


class MyInt(object):
    def __init__(self, n):
        self.int = n

@jit
def fib_obj(n):
    a, b = MyInt(1), MyInt(1)
    for i in range(n.int):
        a.int, b.int = a.int+b.int, a.int

    return a.int

@jit
def fib(n):
    a, b = 1, 1
    for i in range(n):
        a, b = a + b, a
    return a


if __name__ == "__main__":
    fib_obj(MyInt(10))
    fib(10)
