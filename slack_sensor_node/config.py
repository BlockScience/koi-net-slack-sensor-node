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
    slack_bot_token: str | None = "SLACK_BOT_TOKEN"
    slack_signing_secret: str | None = "SLACK_SIGNING_SECRET"
    slack_app_token: str | None = "SLACK_APP_TOKEN"
    
class SlackConfig(BaseModel):
    allowed_channels: list[str] | None = []
    last_processed_ts: str | None = "0"

class SlackSensorNodeConfig(NodeConfig):
    koi_net: KoiNetConfig | None = Field(default_factory = lambda: 
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
    env: SlackEnvConfig | None = Field(default_factory=SlackEnvConfig)
    slack: SlackConfig | None = Field(default_factory=SlackConfig)
