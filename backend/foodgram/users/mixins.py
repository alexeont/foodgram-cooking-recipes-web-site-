from users.validators import validator_username


class UsernameValidatorMixin:
    def validate_username(self, value):
        return validator_username(value)
