class ValidateSetterProperty:
    def __init__(self, func, doc=None):
        self.func = func
        self.__doc__ = doc if doc is not None else func.__doc__

    def __set__(self, obj, value):
        validated_value = self.func(obj, value)
        obj.__dict__[self.name] = validated_value

    def __set_name__(self, owner, name):
        self.name = name