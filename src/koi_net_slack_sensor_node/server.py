from fastapi import Request
from koi_net.entrypoints import NodeServer
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler


class SlackSensorNodeServer(NodeServer):
    def __init__(self, config, response_handler, slack_app):
        super().__init__(config, response_handler)
        self.slack_app = slack_app
    
        @self.app.post("/slack-event-listener")
        async def slack_listener(request: Request):
            return await AsyncSlackRequestHandler(self.slack_app).handle(request)