import base64

from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
from aiohttp_session import new_session, get_session

from app.admin.schemes import AdminRequestSchema, AdminResponseSchema, AdminSchema
from app.store.admin.accessor import AdminAccessor
from app.web.app import View
from app.admin.models import *

from aiohttp_apispec import request_schema, response_schema, docs

from app.web.utils import check_basic_auth, json_response


class AdminLoginView(View):
    @docs(tags=['admin'], summary='Admin log in', description='Log in as admin')
    @request_schema(AdminRequestSchema)
    @response_schema(AdminResponseSchema)
    async def post(self):
        data = await self.request.json()
        admin = await self.request.app.store.admins.get_by_email(data['email'])
        if admin:
            if sha256(str(data['password']).encode()).hexdigest() == admin.password:
                session = await new_session(request=self.request)
                session['email'] = data['email']
                return json_response(data=AdminResponseSchema().dump(admin))
        raise HTTPForbidden


class AdminCurrentView(View):
    @docs(tags=['admin'], summary='Receive yourself data', description='Receive data about yourself(admin) from database')
    @response_schema(AdminResponseSchema)
    async def get(self):
        """if not self.request.headers.get("Authorization"):
            raise HTTPUnauthorized
        if not check_basic_auth(self.request.headers.get("Authorization"),
                                email=self.request.app.config.admin.email,
                                password=self.request.app.config.admin.password):
            raise HTTPForbidden
        """
        if not await get_session(request=self.request):
            raise HTTPUnauthorized

        raw_credentials = self.request.headers.get("Authorization")
        credentials = base64.b64decode(raw_credentials).decode()
        email = credentials.split(':')[0]
        admin = await self.request.app.store.admins.get_by_email(email)
        return json_response(AdminResponseSchema().dump(admin))
