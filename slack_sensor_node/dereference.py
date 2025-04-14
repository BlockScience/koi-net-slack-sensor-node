from rid_lib import RID
from rid_lib.types import SlackMessage, SlackChannel, SlackUser, SlackWorkspace
from rid_lib.ext import Bundle
from koi_net.protocol.api_models import ManifestsPayload, BundlesPayload
from .core import node, slack_app

async def fetch_missing(payload: ManifestsPayload | BundlesPayload):
    found_bundles: list[Bundle] = []
    for rid in payload.not_found:
        if type(rid) not in (
            SlackMessage, SlackChannel, SlackUser, SlackWorkspace
        ): continue
        
        bundle = await dereference(rid)
        if bundle:
            found_bundles.append(bundle)
    
    for bundle in found_bundles:
        payload.not_found.remove(bundle.rid)
        
        if type(payload) == ManifestsPayload:
            payload.manifests.append(bundle.manifest)
            
        elif type(payload) == BundlesPayload:
            payload.bundles.append(bundle)
    
    return payload

async def dereference(rid: RID):
    if type(rid) == SlackMessage:
        resp = await slack_app.client.conversations_replies(
            channel=rid.channel_id,
            ts=rid.ts
        )
        message = resp["messages"][0]
        
        return Bundle.generate(rid, message)
        
    elif type(rid) == SlackChannel:
        resp = await slack_app.client.conversations_info(
            channel=rid.channel_id
        )
        channel = resp["channel"]
        
        return Bundle.generate(rid, channel)
        
    elif type(rid) == SlackUser:
        profile_resp = await slack_app.client.users_profile_get(user=rid.user_id)
        profile = profile_resp["profile"]
        
        user_resp = await slack_app.client.users_info(user=rid.user_id)
        user = user_resp["user"]
        
        user["profile"] = profile
        
        return Bundle.generate(rid, user)
    
    elif type(rid) == SlackWorkspace:
        resp = await slack_app.client.team_info(team=rid.team_id)
        workspace = resp["team"]
        
        return Bundle.generate(rid, workspace)
    
    else:
        raise TypeError(f"RID of type {type(rid)!r} is not allowed")