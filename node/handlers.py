import logging
from koi_net.processor.handler import HandlerType
from koi_net.processor.knowledge_object import KnowledgeSource, KnowledgeObject
from koi_net.processor.interface import ProcessorInterface
from koi_net.protocol.edge import EdgeType
from koi_net.protocol.node import NodeProfile, NodeType
from koi_net.protocol.helpers import generate_edge_bundle
from rid_lib.types import KoiNetNode, SlackMessage
from .core import node

logger = logging.getLogger(__name__)


@node.processor.register_handler(HandlerType.Network, rid_types=[KoiNetNode])
def coordinator_contact(processor: ProcessorInterface, kobj: KnowledgeObject):
    node_profile = kobj.bundle.validate_contents(NodeProfile)
    
    # looking for event provider of nodes
    if KoiNetNode not in node_profile.provides.event:
        return
    
    # already have an edge established
    if processor.network.graph.get_edge_profile(
        source=kobj.rid,
        target=processor.identity.rid,
    ) is not None:
        return
    
    logger.info("Identified a coordinator!")
    logger.info("Proposing new edge")
    
    if processor.identity.profile.node_type == NodeType.FULL:
        edge_type = EdgeType.WEBHOOK
    else:
        edge_type = EdgeType.POLL
    
    # queued for processing
    processor.handle(bundle=generate_edge_bundle(
        source=kobj.rid,
        target=node.identity.rid,
        edge_type=edge_type,
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
        
    if float(msg_rid.ts) < float(processor.config.slack.last_processed_ts):
        return
    
    processor.config.slack.last_processed_ts = msg_rid.ts
    processor.config.save_to_yaml()