from pydantic import BaseModel, Field
from rid_lib.types import (
    SlackMessage, 
    SlackChannel, 
    SlackUser, 
    SlackWorkspace
)
from koi_net.config import (
    FullNodeConfig, 
    KoiNetConfig, 
    FullNodeProfile, 
    NodeProvides,
    EnvConfig
)


class SlackEnvConfig(EnvConfig):
    slack_bot_token: str
    slack_signing_secret: str
    slack_app_token: str
    
class SlackConfig(BaseModel):
    allowed_channels: list[str] = []
    last_processed_ts: str = "0"

class SlackSensorNodeConfig(FullNodeConfig):
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="slack-sensor",
        node_profile=FullNodeProfile(
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
    env: SlackEnvConfig = Field(default_factory=SlackEnvConfig)
    slack: SlackConfig = SlackConfig()
