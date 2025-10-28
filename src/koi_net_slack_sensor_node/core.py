import logging
from fastapi import Request
from koi_net import NodeInterface

from .lifecycle import SlackSensorLifecycle
from .config import SlackSensorNodeConfig

logger = logging.getLogger(__name__)

node = NodeInterface(
    config=SlackSensorNodeConfig.load_from_yaml("config.yaml"),
    use_kobj_processor_thread=True,
    NodeLifecycleOverride=SlackSensorLifecycle
)

from . import handlers

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler

slack_app = AsyncApp(
    token=node.config.env.slack_bot_token,
    signing_secret=node.config.env.slack_signing_secret
)

async_slack_handler = AsyncSlackRequestHandler(slack_app)

node.lifecycle.set_slack_app(slack_app)

@node.server.app.post("/slack-event-listener")
async def slack_listener(request: Request):
    return await async_slack_handler.handle(request)

from . import slack_event_handlers