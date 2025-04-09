import logging
from rid_lib.ext import Bundle
from rid_lib.types import SlackMessage
from koi_net.protocol.event import EventType
from .core import node, slack_app
from .config import OBSERVING_CHANNELS

logger = logging.getLogger(__name__)


@slack_app.event("message")
async def handle_message_event(event):
    # with open("slack_sensor/message.json", "w") as f:
    #     json.dump(event, f, indent=2)

    subtype = event.get("subtype")
    # new message
    if not subtype:
        message_rid = SlackMessage(
            team_id=event["team"],
            channel_id=event["channel"],
            ts=event["ts"]
        )
        
        if message_rid.channel_id not in OBSERVING_CHANNELS:
            return
        
        # normalize to non event message structure
        data = event
        del data["channel"]
        del data["event_ts"]
        del data["channel_type"]
        
        msg_bundle = Bundle.generate(
            rid=message_rid,
            contents=data
        )
        
        logger.info(f"Handling new Slack message {message_rid!r}")
        
        node.processor.handle(bundle=msg_bundle)
        
    
    elif subtype == "message_changed":
        message_rid = SlackMessage(
            team_id=event["message"]["team"],
            channel_id=event["channel"],
            ts=event["message"]["ts"]
        )
        # normalize to non event message structure
        data = event["message"]
        del data["source_team"]
        del data["user_team"]
        
        msg_bundle = Bundle.generate(
            rid=message_rid,
            contents=data
        )
        
        logger.info(f"Handling updated Slack message {message_rid!r}")
        
        node.processor.handle(bundle=msg_bundle)
    
    elif subtype == "message_deleted":
        message_rid = SlackMessage(
            team_id=event["previous_message"]["team"],
            channel_id=event["channel"],
            ts=event["previous_message"]["ts"]
        )
        
        logger.info(f"Handling deleted Slack message {message_rid!r}")
        
        node.processor.handle(
            rid=message_rid,
            event_type=EventType.FORGET)
    
    else:
        logger.info(f"Ignoring unsupport Slack message subtype {subtype}")
        return    