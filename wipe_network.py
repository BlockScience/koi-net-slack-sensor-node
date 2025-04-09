from slack_sensor_node.core import node
from rid_lib.types import KoiNetEdge, KoiNetNode

for rid in node.cache.list_rids(rid_types=[KoiNetNode, KoiNetEdge]):
    node.cache.delete(rid)