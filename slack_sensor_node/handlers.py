import logging
from koi_net.processor.handler import HandlerType
from koi_net.processor.knowledge_object import KnowledgeObject
from koi_net.processor.interface import ProcessorInterface
from rid_lib.types import SlackMessage
from .core import node

logger = logging.getLogger(__name__)

    
@node.processor.register_handler(HandlerType.RID, rid_types=[SlackMessage])
def update_last_processed_ts(processor: ProcessorInterface, kobj: KnowledgeObject):
    msg_rid: SlackMessage = kobj.rid
        
    if float(msg_rid.ts) < float(processor.config.slack.last_processed_ts):
        return
    
    processor.config.slack.last_processed_ts = msg_rid.ts
    processor.config.save_to_yaml()