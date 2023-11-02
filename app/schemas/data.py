from marshmallow import Schema, fields


class DataSchema(Schema):
    timestamp = fields.DateTime()
    value = fields.Float()
    field = fields.String()
