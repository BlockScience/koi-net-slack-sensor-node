from typing import cast
from dataclasses import dataclass

from rid_lib.types import SlackMessage
from koi_net.components.interfaces import HandlerType, KnowledgeHandler
from koi_net.protocol import KnowledgeObject

from .config import SlackSensorNodeConfig


@dataclass
class LastProcessedTSHandler(KnowledgeHandler):
    config: SlackSensorNodeConfig
    
    handler_type = HandlerType.RID
    rid_types = (SlackMessage,)
    
    def handle(self, kobj: KnowledgeObject):
        msg_rid = cast(SlackMessage, kobj.rid)
        if float(msg_rid.ts) < float(self.config.slack.last_processed_ts):
            return
        
        self.config.slack.last_processed_ts = msg_rid.ts
        self.config.save_to_yaml()