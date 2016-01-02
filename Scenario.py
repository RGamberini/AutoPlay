class Scenario(object):
    """A basic Scenario for GameScraper"""
    def __init__(self, items, validateFunction=None, types=None):
        self.items = items
        if validateFunction is not None:
            self.validate = validateFunction
        if types is not None:
            self.types.update(types)

    def parseInt(n):
        return int(n)

    def parseString(s):
        return s

    types = {
    "int": parseInt,
    "string": parseString,
    }

    def parse(self, item, _type):
        return self.types[_type](item)

    def validate(self, items):
        print("No validation function defined returning false")
        return False
