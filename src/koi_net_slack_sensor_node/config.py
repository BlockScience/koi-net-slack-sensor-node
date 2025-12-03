from pydantic import BaseModel
from rid_lib.types import (
    SlackMessage, 
    SlackChannel, 
    SlackUser, 
    SlackWorkspace
)
from koi_net.config.core import EnvConfig
from koi_net.config.full_node import (
    FullNodeConfig, 
    KoiNetConfig, 
    NodeProfile, 
    NodeProvides
)


class SlackEnvConfig(EnvConfig):
    slack_bot_token: str = "SLACK_BOT_TOKEN"
    slack_signing_secret: str = "SLACK_SIGNING_SECRET"
    slack_app_token: str = "SLACK_APP_TOKEN"
    
class SlackConfig(BaseModel):
    allowed_channels: list[str] = []
    last_processed_ts: str = "0"

class SlackSensorNodeConfig(FullNodeConfig):
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="slack-sensor",
        node_profile=NodeProfile(
            provides=NodeProvides(
                event=[
                    SlackMessage
                ],
                state=[
                    SlackMessage, 
                    SlackUser, 
                    SlackChannel, 
                    SlackWorkspace
                ]
            )
        )
    )
    env: SlackEnvConfig = SlackEnvConfig()
    slack: SlackConfig = SlackConfig()
