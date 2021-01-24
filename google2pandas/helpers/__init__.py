class ValidateSetterProperty:
    def __init__(self, func, doc=None):
        self.func = func
        self.__doc__ = doc if doc is not None else func.__doc__

    def __set__(self, obj, value):
        validated_value = self.func(obj, value)
        obj.__dict__[self.name] = validated_value

    def __set_name__(self, owner, name):
        self.name = name


def scope_validation(new_scopes, possbile_scopes):
    if isinstance(new_scopes, list):
        for scope in new_scopes:
            if scope not in new_scopes:
                raise ValueError(
                    "A value within the sheet_scopes variable is not valid\n"
                    "Check here for possible scope values https://developers.google.com/sheets/api/guides/authorizing"
                )

    elif isinstance(new_scopes, str):
        if new_scopes not in possbile_scopes:
            raise ValueError(
                "The sheet_scopes variable is not valid\n"
                "Check here for possible scope values https://developers.google.com/sheets/api/guides/authorizing"
            )

    else:
        raise TypeError("The sheet_scopes variable should be of type list or str")
    return new_scopes