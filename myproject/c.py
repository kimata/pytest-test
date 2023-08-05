class C:
    def __init__(self):
        self.prop_ = "prop C"

    @property
    def prop(self):
        return self.prop_

    def c_func(self):
        return "called C.c_func"
