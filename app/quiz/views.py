from aiohttp.web_exceptions import HTTPConflict, HTTPUnauthorized, HTTPForbidden, HTTPBadRequest, HTTPNotFound, \
    HTTPInternalServerError
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import get_session

from app.quiz.schemes import (
    ThemeSchema, ThemeRequestSchema, QuestionSchema, ListQuestionSchema, ThemeIdSchema, QuestionResponseSchema
)
from app.web.app import View
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response, check_basic_auth


async def is_authorized(request):
    """if not request.headers.get("Authorization"):
        raise HTTPUnauthorized
    if not check_basic_auth(request.headers.get("Authorization"),
                            email=request.app.config.admin.email,
                            password=request.app.config.admin.password):
        raise HTTPForbidden"""
    if await get_session(request=request):
        return
    raise HTTPUnauthorized


class ThemeAddView(View):
    @docs(tags=['theme'], summary='Add new theme', description='Add new theme to database')
    @request_schema(ThemeRequestSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        await is_authorized(self.request)

        title = self.data['title']
        theme_exists = await self.store.quizzes.get_theme_by_title(title)
        if theme_exists:
            raise HTTPConflict
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(View):
    @docs(tags=['theme'], summary='List themes', description='List themes from database')
    @response_schema(ThemeSchema, 200)
    async def get(self):
        await is_authorized(self.request)

        themes = await self.store.quizzes.list_themes()
        raw_themes = [ThemeSchema().dump(theme) for theme in themes]
        return json_response(data={"themes": raw_themes})


class QuestionAddView(View):
    @docs(tags=['question'], summary='Add question', description='Add question to database')
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        await is_authorized(self.request)

        data = self.request['data']
        await self.question_validation(data)
        question = await self.store.quizzes.create_question(
            title=data['title'],
            theme_id=data['theme_id'],
            answers=data['answers']
        )
        return json_response(data=QuestionSchema().dump(question))

    async def question_validation(self, data):
        if not await self.store.quizzes.get_theme_by_id(data['theme_id']):
            raise HTTPNotFound
        if await self.store.quizzes.get_question_by_title(data['title']):
            raise HTTPConflict
        if sum([answer['is_correct'] for answer in data['answers']]) != 1:
            raise HTTPBadRequest
        if len(data['answers']) < 2:
            raise HTTPBadRequest


class QuestionListView(View):
    @docs(tags=['question'], summary='Add question', description='Add question to database')
    @request_schema(ThemeIdSchema)
    @response_schema(QuestionSchema, 200)
    async def get(self):
        await is_authorized(self.request)

        try:
            theme_id = int(self.request.query['theme_id'])
        except:
            theme_id = False
        if theme_id:
            questions = await self.store.quizzes.list_questions_by_theme(theme_id=theme_id)
            raw_questions = [QuestionSchema().dump(question) for question in questions]
            return json_response(data={"questions": raw_questions})
        questions = await self.store.quizzes.list_questions()
        raw_questions = [QuestionSchema().dump(question) for question in questions]
        return json_response(data={"questions": raw_questions})


