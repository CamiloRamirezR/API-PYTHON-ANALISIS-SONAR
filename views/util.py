import json
from .schemas.post_schemas import ErrorResponseSchema
from marshmallow import ValidationError


def class_route(self, rule, **options):
    def decorator(cls):
        self.add_url_rule(rule, view_func=cls.as_view(cls.__name__), **options)
        return cls

    return decorator


def create_error_response(message):
    if isinstance(message, ValidationError):
        error = {"msg": message.normalized_messages()}
    else:
        error = {"msg": message}
    return ErrorResponseSchema().dumps(error)

