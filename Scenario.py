class Scenario(object):
    """A basic Scenario for GameScraper"""
    def __init__(self, items, validateFunction, types=None):
        self.validate = validateFunction
        self.items = items
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

    def parse(self, item):
        return self.types[item["type"]](item["value"])

    def validate(self, items):
        print("No validation function defined returning false")
        return False
