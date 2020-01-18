import types


ALL_CONSTANTS = {}


class ModuleWithConstants(types.ModuleType):
    def __setattr__(self, attr, value, final=False):
        if self.__file__ not in ALL_CONSTANTS:
            ALL_CONSTANTS[self.__file__] = {}

        if attr in ALL_CONSTANTS[self.__file__] and not final:
            print(
                "You cannot change the value of %s.%s to %s"
                % (self.__name__, attr, value)
            )
        else:
            if final or attr == attr.upper():
                ALL_CONSTANTS[self.__file__][attr] = value
            super().__setattr__(attr, value)
