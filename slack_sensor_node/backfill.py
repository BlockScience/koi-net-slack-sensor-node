import asyncio
from slack_sdk.errors import SlackApiError
from rid_lib.ext import Bundle
from rid_lib.types import SlackMessage
from .core import node, slack_app
from .config import OBSERVING_CHANNELS


async def auto_retry(function, **params):
    try:
        return await function(**params)
    except SlackApiError as e:
        if e.response["error"] == "ratelimited":
            retry_after = int(e.response.headers["Retry-After"])
            print(f"timed out, waiting {retry_after} seconds")
            await asyncio.sleep(retry_after)
            return await function(**params)
        else:
            print("unknown error", e)
            quit()

async def backfill_messages(channel_ids: list[str] = [], after=0):
    resp = await slack_app.client.team_info()
    team = resp.data["team"]
    team_id = team["id"]

    channels = [{"id": cid} for cid in channel_ids]
    
    # get list of channels
    channel_cursor = None
    while not channels or channel_cursor:
        resp = await slack_app.client.conversations_list(cursor=channel_cursor)
        result = resp.data
        channels.extend(result["channels"])
        channel_cursor = result.get("response_metadata", {}).get("next_cursor")

    for channel in channels:
        channel_id = channel["id"]
        
        print(channel_id)

        # get list of messages in channel
        message_cursor = None
        messages = []
        while not messages or message_cursor:
            result = await auto_retry(slack_app.client.conversations_history,
                channel=channel_id,
                limit=500,
                cursor=message_cursor,
                oldest=after
            )
            
            if not result["messages"]: break
            
            messages.extend(result["messages"])
            if result["has_more"]:
                message_cursor = result["response_metadata"]["next_cursor"]
            else:
                message_cursor = None


        for message in messages:
            message_rid = SlackMessage(team_id, channel_id, message["ts"])
            
            if message.get("subtype") is None:
                
                message_bundle = Bundle.generate(
                    rid=message_rid,
                    contents=message
                )
                
                node.processor.handle(bundle=message_bundle)                
            
            thread_ts = message.get("thread_ts")
            
            # ignore threaded messages sent to channel (double counted within thread)
            if thread_ts and (thread_ts != message["ts"]):
                continue

            if thread_ts:
                threaded_message_cursor = None
                threaded_messages = []
                while not threaded_messages or threaded_message_cursor:
                    result = await auto_retry(slack_app.client.conversations_replies,
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
                        
                print(message_rid, "thread with", len(threaded_messages), "messages")
                
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
                        
                        node.processor.handle(bundle=threaded_message_bundle)     

    print("done")
    node.processor.flush_kobj_queue()
                        
if __name__ == "__main__":
    node.initialize()
    
    asyncio.run(
        backfill_messages(
            channel_ids=OBSERVING_CHANNELS))