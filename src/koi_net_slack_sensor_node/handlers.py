import logging
from koi_net.context import HandlerContext
from koi_net.processor.handler import HandlerType
from koi_net.processor.knowledge_object import KnowledgeObject
from rid_lib.types import SlackMessage
from .core import node

logger = logging.getLogger(__name__)

    
@node.pipeline.register_handler(HandlerType.RID, rid_types=[SlackMessage])
def update_last_processed_ts(ctx: HandlerContext, kobj: KnowledgeObject):
    msg_rid: SlackMessage = kobj.rid
        
    if float(msg_rid.ts) < float(ctx.config.slack.last_processed_ts):
        return
    
    ctx.config.slack.last_processed_ts = msg_rid.ts
    ctx.config.save_to_yaml()