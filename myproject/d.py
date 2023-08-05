import c
import c as c2


class D:
    def __init__(self):
        self.c = c.C()
        self.c2 = c2.C()

    def d_func(self):
        return self.c.c_func()

    def d_func2(self):
        return self.c2.c_func()
