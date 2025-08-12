from pydantic import BaseModel, Field
from koi_net.protocol.node import NodeProfile, NodeType, NodeProvides
from koi_net.config import NodeConfig, EnvConfig, KoiNetConfig
from rid_lib.types import (
    SlackMessage, 
    SlackChannel, 
    SlackUser, 
    SlackWorkspace
)


class SlackEnvConfig(EnvConfig):
    slack_bot_token: str = "SLACK_BOT_TOKEN"
    slack_signing_secret: str = "SLACK_SIGNING_SECRET"
    slack_app_token: str = "SLACK_APP_TOKEN"
    
class SlackConfig(BaseModel):
    allowed_channels: list[str] = []
    last_processed_ts: str = "0"

class SlackSensorNodeConfig(NodeConfig):
    koi_net: KoiNetConfig = Field(default_factory = lambda: 
        KoiNetConfig(
            node_name="slack-sensor",
            node_profile=NodeProfile(
                node_type=NodeType.FULL,
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
    )
    env: SlackEnvConfig = Field(default_factory=SlackEnvConfig)
    slack: SlackConfig = Field(default_factory=SlackConfig)
