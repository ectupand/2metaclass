from marshmallow import Schema, fields


class ThemeSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)


class ThemeRequestSchema(Schema):
    title = fields.Str(required=True)


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Boolean(required=True)


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested(AnswerSchema, many=True)


class QuestionResponseSchema(QuestionSchema):
    pass


class ThemeListSchema(Schema):
    pass


class ThemeIdSchema(Schema):
    theme_id = fields.Int(required=False)


class ListQuestionSchema(Schema):
    pass

