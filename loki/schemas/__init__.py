from marshmallow import Schema
from marshmallow import pre_load, post_dump


class BaseSchema(Schema):
    __envelope__ = {"single": None, "many": None}

    def get_envelope_key(self, many):
        key = self.__envelope__["many"] if many else self \
            .__envelope__["single"]
        assert key is not None, "Envelope key undefined"
        return key

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        key = self.get_envelope_key(many)
        return data[key]

    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many, **kwargs):
        key = self.get_envelope_key(many)
        return {key: data}
