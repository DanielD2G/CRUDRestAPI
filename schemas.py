from marshmallow import Schema, fields


class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    fullname = fields.Str(required=True)
    photo = fields.Str(required=False)


class UserUpdateSchema(Schema):
    username = fields.Str()
    password = fields.Str(load_only=True)
    fullname = fields.Str()
    photo = fields.Str()


class LoginUserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainPostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    priority = fields.Str(required=True)
    status = fields.Boolean(required=True)


class PostUpdateSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    priority = fields.Str(required=True)
    status = fields.Boolean(required=True)


class PostSchema(PlainPostSchema):
    user = fields.Nested(PlainUserSchema(), dump_only=True)


class UserSchema(PlainUserSchema):
    posts = fields.List(fields.Nested(PlainPostSchema(), dump_only=True))


class ShowPostSchema(PlainPostSchema):
    created = fields.DateTime()
    updated = fields.DateTime()
