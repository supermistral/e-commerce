
class CleanMixin:

    def clean_method(self, value: str) -> str:
        return value.upper()

    def clean_path(self, value: str) -> str:
        if not value.startswith('/'):
            return '/' + value
        return value


class ValidateMixin:

    def validate_method(self, value: str) -> bool:
        return value.lower() in ['get', 'post', 'delete', 'put', 'patch']

    def validate_path(self, value: str) -> bool:
        parts = value.split('/')

        for part in parts:
            if not part or part.isalnum() or part[0] == '{' and part[-1] == '}':
                continue
            else:
                return False

        return True
