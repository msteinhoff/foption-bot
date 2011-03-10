class Singleton(object):
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it
    def init(self, *args, **kwds):
        pass


def __new__(cls):
    """
    The singleton
    """
    inst = cls.__dict__.get("__inst__")
    
    if inst != None:
        return inst
    
    cls.__inst__ = inst = object.__new__(cls)
    
    return inst

