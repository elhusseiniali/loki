from loki.schemas import BaseSchema
from marshmallow import fields, post_load
from loki.services.users import user_service


class UserSchema(BaseSchema):
    __envelope__ = {"single": "user", "many": "users"}

    class Meta:
        ordered = True

    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    image_file = fields.String(required=False)

    @post_load
    def make_object(self, data, **kwargs):
        return user_service.create_user(**data)
