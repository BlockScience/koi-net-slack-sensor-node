import logging
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from koi_net import NodeInterface
from koi_net.network import NetworkInterface
from .config import SlackSensorNodeConfig

logger = logging.getLogger(__name__)


node = NodeInterface(
    config=SlackSensorNodeConfig.load_from_yaml("config.yaml"),
    use_kobj_processor_thread=True
)

(node.config.env.slack_bot_token)

network = NetworkInterface(node.config, node.cache, node.identity)
network.config.env
node.config.env.slack_app_token

from . import handlers

slack_app = AsyncApp(
    token=node.config.env.slack_bot_token,
    signing_secret=node.config.env.slack_signing_secret
)

async_slack_handler = AsyncSlackRequestHandler(slack_app)

from . import slack_event_handlers