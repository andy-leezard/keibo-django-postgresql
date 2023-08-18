import json
import random
import string
from django.urls.converters import IntConverter
from typing import Any, Union


# Converts string parameter into int (it covers strings of negative ints)
class NegativeIntConverter(IntConverter):
    regex = '-?\d+'  # type: ignore

    def to_python(self, value: str) -> int:
        return int(value)

    def to_url(self, value: int) -> str:
        return str(value)


def safely_load_json(data: str, fallback: Any = None) -> Union[Any, dict, list]:
    """
    Attempt to load a JSON string. If it fails, return the provided fallback value.
    :param data: The JSON string to parse.
    :param fallback: The value to return if parsing fails.
    :return: The parsed JSON data or the fallback value if parsing fails.
    """
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return fallback

# Create this outside the function to avoid re-creation on each function call
LETTERS_AND_DIGITS = string.ascii_letters + string.digits

def generate_random_string(length=6, prefix="", suffix=""):
    return prefix + ''.join(random.choice(LETTERS_AND_DIGITS) for _ in range(length)) + suffix