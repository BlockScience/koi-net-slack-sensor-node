import asyncio

import structlog
from koi_net.core import KobjQueue
from slack_bolt.async_app import AsyncApp
from slack_sdk.errors import SlackApiError
from rid_lib.ext import Bundle
from rid_lib.types import SlackMessage

from .config import SlackSensorNodeConfig

log = structlog.stdlib.get_logger()


class Backfiller:
    def __init__(
        self,
        slack_app: AsyncApp,
        config: SlackSensorNodeConfig,
        kobj_queue: KobjQueue
    ):
        self.slack_app = slack_app
        self.config = config
        self.kobj_queue = kobj_queue
        
    def start(self):
        asyncio.run(self.backfill_messages())

    async def auto_retry(self, function, **kwargs):
        try:
            return await function(**kwargs)
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                retry_after = int(e.response.headers["Retry-After"])
                log.info(f"timed out, waiting {retry_after} seconds")
                await asyncio.sleep(retry_after)
                return await function(**kwargs)
            elif e.response["error"] == "not_in_channel":
                log.info(f"not in channel {kwargs['channel']}, attempting to join")
                await self.slack_app.client.conversations_join(channel=kwargs["channel"])
                return await function(**kwargs)
            else:
                log.warning("unknown error", e)
                quit()

    async def backfill_messages(self):
        resp = await self.slack_app.client.team_info()
        team = resp.data["team"]
        team_id = team["id"]

        channels = [{"id": cid} for cid in self.config.slack.allowed_channels]
        
        log.info("Scanning for channels")
        
        # get list of channels
        channel_cursor = None
        while not channels or channel_cursor:
            resp = await self.slack_app.client.conversations_list(cursor=channel_cursor)
            result = resp.data
            channels.extend(result["channels"])
            log.info(f"Found {len(result['channels'])} channels")
            channel_cursor = result.get("response_metadata", {}).get("next_cursor")

        log.info(f"Scanning {len(channels)} channels for messages")
        for channel in channels:
            channel_id = channel["id"]
            
            log.info(f"Scanning {channel_id}...")

            # get list of messages in channel
            message_cursor = None
            messages = []
            while not messages or message_cursor:
                result = await self.auto_retry(self.slack_app.client.conversations_history,
                    channel=channel_id,
                    limit=500,
                    cursor=message_cursor,
                    oldest=self.config.slack.last_processed_ts
                )
                
                if not result["messages"]: break
                
                messages.extend(result["messages"])
                log.info(f"Found {len(result['messages'])} messages")
                if result["has_more"]:
                    message_cursor = result["response_metadata"]["next_cursor"]
                else:
                    message_cursor = None

            log.info(f"Scanning {len(messages)} messages")
            messages.reverse()
            for message in messages:
                message_rid = SlackMessage(team_id, channel_id, message["ts"])
                
                if message.get("subtype") is None:
                    
                    message_bundle = Bundle.generate(
                        rid=message_rid,
                        contents=message
                    )
                    log.info(f"{message_rid}")
                    self.kobj_queue.push(bundle=message_bundle)
                
                thread_ts = message.get("thread_ts")
                
                # ignore threaded messages sent to channel (double counted within thread)
                if thread_ts and (thread_ts != message["ts"]):
                    continue

                if thread_ts:
                    threaded_message_cursor = None
                    threaded_messages = []
                    while not threaded_messages or threaded_message_cursor:
                        result = await self.auto_retry(self.slack_app.client.conversations_replies,
                            channel=channel_id,
                            ts=thread_ts,
                            limit=500,
                            cursor=threaded_message_cursor
                        )
                                
                        threaded_messages.extend(result["messages"])
                        
                        if result["has_more"]:
                            threaded_message_cursor = result["response_metadata"]["next_cursor"]
                        else:
                            threaded_message_cursor = None
                            
                    log.info(f"{message_rid} thread with {len(threaded_messages)} messages")
                    
                    # don't double count thread parent message
                    for threaded_message in threaded_messages[1:]:
                        threaded_message_rid = SlackMessage(
                            team_id, 
                            channel_id, 
                            threaded_message["ts"]
                        )
                        if threaded_message.get("subtype") is None:
                            threaded_message_bundle = Bundle.generate(
                                rid=threaded_message_rid,
                                contents=threaded_message
                            )
                            
                            log.info(f"{threaded_message_rid}")
                            self.kobj_queue.push(bundle=threaded_message_bundle)     

        log.info("done")