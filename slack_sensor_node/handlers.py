import logging
import json
from koi_net.processor.handler import HandlerType
from koi_net.processor.knowledge_object import KnowledgeSource, KnowledgeObject
from koi_net.processor.interface import ProcessorInterface
from koi_net.protocol.event import EventType
from koi_net.protocol.edge import EdgeType
from koi_net.protocol.node import NodeProfile
from koi_net.protocol.helpers import generate_edge_bundle
from rid_lib.types import KoiNetNode, SlackMessage
from .config import LAST_PROCESSED_TS
from .core import node

logger = logging.getLogger(__name__)


@node.processor.register_handler(HandlerType.Network, rid_types=[KoiNetNode])
def coordinator_contact(processor: ProcessorInterface, kobj: KnowledgeObject):
    # when I found out about a new node
    if kobj.normalized_event_type != EventType.NEW: 
        return
    
    node_profile = kobj.bundle.validate_contents(NodeProfile)
    
    # looking for event provider of nodes
    if KoiNetNode not in node_profile.provides.event:
        return
    
    logger.info("Identified a coordinator!")
    logger.info("Proposing new edge")
    
    # queued for processing
    processor.handle(bundle=generate_edge_bundle(
        source=kobj.rid,
        target=node.identity.rid,
        edge_type=EdgeType.WEBHOOK,
        rid_types=[KoiNetNode]
    ))
    
    logger.info("Catching up on network state")
    
    payload = processor.network.request_handler.fetch_rids(kobj.rid, rid_types=[KoiNetNode])
    for rid in payload.rids:
        if rid == processor.identity.rid:
            logger.info("Skipping myself")
            continue
        if processor.cache.exists(rid):
            logger.info(f"Skipping known RID '{rid}'")
            continue
        
        # marked as external since we are handling RIDs from another node
        # will fetch remotely instead of checking local cache
        processor.handle(rid=rid, source=KnowledgeSource.External)
    logger.info("Done")
    
@node.processor.register_handler(HandlerType.RID, rid_types=[SlackMessage])
def update_last_processed_ts(processor: ProcessorInterface, kobj: KnowledgeObject):
    msg_rid: SlackMessage = kobj.rid
    ts = float(msg_rid.ts)
    
    global LAST_PROCESSED_TS
    if ts < LAST_PROCESSED_TS: 
        logger.warning(f"{ts} smaller")
        return
    
    logger.warning(f"{ts} larger")
    LAST_PROCESSED_TS = ts
    
    with open("state.json", "w") as f:
        json.dump({"last_processed_ts": LAST_PROCESSED_TS}, f)