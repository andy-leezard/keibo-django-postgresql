from django.urls.converters import IntConverter


# Converts string parameter into int (it covers strings of negative ints)
class NegativeIntConverter(IntConverter):
    regex = '-?\d+'

    def to_python(self, value: str) -> int:
        return int(value)

    def to_url(self, value: int) -> str:
        return str(value)
