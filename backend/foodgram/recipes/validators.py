from django.core.exceptions import ValidationError

from foodgram.constants import INVALID_COLOR_FIELD_ERROR_TEXT


def validate_color(value):
    if (len(value) != 7 or value[0] != '#'):
        raise ValidationError(INVALID_COLOR_FIELD_ERROR_TEXT)
    return value
