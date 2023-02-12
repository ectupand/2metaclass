import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    email: str
    password: str


@dataclass
class BotConfig:
    token: str
    group_id: str


@dataclass
class Config:
    admin: AdminConfig
    session: SessionConfig = None
    bot: BotConfig = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        config_raw = yaml.safe_load(f)

    app.config = Config(
        admin=AdminConfig(
            email=config_raw["admin"]["email"],
            password=config_raw["admin"]["password"],
        ),
        session=SessionConfig(
            key=config_raw["session"]["key"]
        ),
        bot=BotConfig(
            token=config_raw["bot"]["token"],
            group_id=config_raw["bot"]["group_id"]
        )
    )
