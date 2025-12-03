from koi_net.core import FullNode
from slack_bolt.async_app import AsyncApp

from .backfill import Backfiller
from .server import SlackSensorNodeServer
from .config import SlackSensorNodeConfig
from .handlers import update_last_processed_ts
from .slack_event_handler import SlackEventHandler


class SlackSensorNode(FullNode):
    config_schema = SlackSensorNodeConfig
    
    slack_app = lambda config: AsyncApp(
        token=config.env.slack_bot_token,
        signing_secret=config.env.slack_signing_secret
    )
    
    server = SlackSensorNodeServer
    backfiller = Backfiller
    slack_event_handler = SlackEventHandler
    
    knowledge_handlers = FullNode.knowledge_handlers + [
        update_last_processed_ts
    ]