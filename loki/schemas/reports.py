from loki.schemas import BaseSchema
from marshmallow import fields, post_load
from loki.services.reports import report_service


class ReportSchema(BaseSchema):
    __envelope__ = {"single": "report", "many": "reports"}

    class Meta:
        ordered = True

    model_id = fields.String(required=False)
    pretrained_classifier = fields.String(required=False)
    data = fields.Dict(required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return report_service.create_report(**data)
