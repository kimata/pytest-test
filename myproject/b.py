import a
from a import a_func


def b_func():
    return a.a_func()


def b_func2():
    return a_func()
