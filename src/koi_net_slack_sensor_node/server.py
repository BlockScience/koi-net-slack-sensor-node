from dataclasses import dataclass

from fastapi import Request
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from koi_net.components import NodeServer


@dataclass
class SlackSensorNodeServer(NodeServer):
    slack_app: AsyncApp
    
    def __post_init__(self):
        super().__post_init__()
        
        @self.app.post("/slack-event-listener")
        async def slack_listener(request: Request):
            return await AsyncSlackRequestHandler(self.slack_app).handle(request)