from koi_net.core import FullNode
from slack_bolt.async_app import AsyncApp

from .backfiller import Backfiller
from .server import SlackSensorNodeServer
from .config import SlackSensorNodeConfig
from .last_processed_ts_handler import LastProcessedTSHandler
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
    
    last_processed_ts_handler = LastProcessedTSHandler