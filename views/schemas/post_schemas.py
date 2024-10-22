from marshmallow import Schema, fields


class CreatePostSchema(Schema):
    routeId = fields.Str(required=True)
    userId = fields.Str(required=True)
    expireAt = fields.DateTime(required=True)
    createdAt = fields.DateTime(required=True)


class ErrorResponseSchema(Schema):
    msg = fields.Raw()



class ResetPostsResponseSchema(Schema):
    msg = fields.String()
