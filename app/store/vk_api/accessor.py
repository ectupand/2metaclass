import typing
from typing import Optional

from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, UpdateMessage
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession()
        await self._get_long_poll_service()
        self.poller = Poller(self.app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        query = self._build_query(host='https://api.vk.com/method/',
                                method='groups.getLongPollServer',
                                params={
                                    'access_token': self.app.config.bot.token,
                                    'group_id': self.app.config.bot.group_id,
                                })
        response = await self.session.get(query)
        json_data = await response.json()
        self.key = json_data['response']['key']
        self.server = json_data['response']['server']
        self.ts = json_data['response']['ts']

    async def poll(self):
        query = self._build_query(host=self.server,
                                  method='',
                                  params={
                                      'act': 'a_check',
                                      'key': self.key,
                                      'ts': self.ts,
                                      'wait': 5
                                  })
        response = await self.session.get(query)
        json_data = await response.json()
        self.ts = json_data['ts']
        raw_updates = json_data['updates']
        updates=[]
        for raw_update in raw_updates:
            message = raw_update['object']['message']
            update = Update(
                type=raw_update['type'],
                object=UpdateObject(
                    message=UpdateMessage(
                        from_id=message['from_id'],
                        text=message['text'],
                        id=message['id']
                    )
                )
            )
            updates.append(update)
        return updates

    async def send_message(self, message: Message) -> None:
        query = self._build_query(host='https://api.vk.com/method/',
                                  method='messages.send',
                                  params={
                                      'peer_id': message.user_id,
                                      'message': message.text,
                                      'access_token': self.app.config.bot.token,
                                  })
        await self.session.get(query)
