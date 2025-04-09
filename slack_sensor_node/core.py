import logging
import threading
import queue
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from rid_lib.types import (
    SlackWorkspace,
    SlackChannel,
    SlackUser,
    SlackMessage
)
from koi_net import NodeInterface
from koi_net.protocol.node import NodeProfile, NodeType, NodeProvides
from .config import URL, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, FIRST_CONTACT

logger = logging.getLogger(__name__)


node = NodeInterface(
    name="slack-sensor",
    profile=NodeProfile(
        base_url=URL,
        node_type=NodeType.FULL,
        provides=NodeProvides(
            event=[SlackMessage],
            state=[SlackMessage, SlackUser, SlackChannel, SlackWorkspace]
        )
    ),
    first_contact=FIRST_CONTACT
)

from . import handlers

def process_kobj_worker():
    while True:        
        try:
            kobj = node.processor.kobj_queue.get(timeout=0.1)
            logger.info(f"Dequeued {kobj!r}")
            node.processor.process_kobj(kobj)
            node.processor.kobj_queue.task_done()
            
        except queue.Empty:
            pass
        
        except Exception as e:
            logger.warning(f"Error processing kobj: {e}")

knowledge_procesor_thread = threading.Thread(target=process_kobj_worker, daemon=True)

slack_app = AsyncApp(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

async_slack_handler = AsyncSlackRequestHandler(slack_app)

from . import slack_event_handlers