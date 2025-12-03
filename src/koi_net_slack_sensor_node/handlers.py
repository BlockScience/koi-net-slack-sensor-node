from koi_net.processor.context import HandlerContext
from koi_net.processor.handler import HandlerType
from koi_net.processor.knowledge_object import KnowledgeObject
from koi_net.processor.handler import KnowledgeHandler
from rid_lib.types import SlackMessage

from .config import SlackSensorNodeConfig


@KnowledgeHandler.create(HandlerType.RID, rid_types=[SlackMessage])
def update_last_processed_ts(ctx: HandlerContext, kobj: KnowledgeObject):
    msg_rid: SlackMessage = kobj.rid
    
    config: SlackSensorNodeConfig = ctx.config
    
    if float(msg_rid.ts) < float(config.slack.last_processed_ts):
        return
    
    config.slack.last_processed_ts = msg_rid.ts
    ctx.config_loader.save_to_yaml()