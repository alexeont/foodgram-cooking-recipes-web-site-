import re

from django.core.exceptions import ValidationError

from foodgram.constants import INVALID_COLOR_FIELD_ERROR_TEXT


def validate_color(value):
    if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$'):
        raise ValidationError(INVALID_COLOR_FIELD_ERROR_TEXT)
    return value
