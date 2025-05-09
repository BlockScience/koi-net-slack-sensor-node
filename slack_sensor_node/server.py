import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Request
from koi_net.processor.knowledge_object import KnowledgeSource
from koi_net.protocol.api_models import (
    PollEvents,
    FetchRids,
    FetchManifests,
    FetchBundles,
    EventsPayload,
    RidsPayload,
    ManifestsPayload,
    BundlesPayload
)
from koi_net.protocol.consts import (
    BROADCAST_EVENTS_PATH,
    POLL_EVENTS_PATH,
    FETCH_RIDS_PATH,
    FETCH_MANIFESTS_PATH,
    FETCH_BUNDLES_PATH
)
from .core import node, async_slack_handler
from .dereference import fetch_missing
from . import backfill


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):    
    node.start()
    
    asyncio.create_task(
        backfill.backfill_messages(node.config)
    )
    
    yield
    node.stop()

app = FastAPI(
    lifespan=lifespan, 
    title="KOI-net Protocol API",
    version="1.0.0"
)


@app.post("/slack-event-listener")
async def slack_listener(request: Request):
    return await async_slack_handler.handle(request)

koi_net_router = APIRouter(
    prefix="/koi-net"
)

@koi_net_router.post(BROADCAST_EVENTS_PATH)
async def broadcast_events(req: EventsPayload):
    logger.info(f"Request to {BROADCAST_EVENTS_PATH}, received {len(req.events)} event(s)")
    for event in req.events:
        node.processor.handle(event=event, source=KnowledgeSource.External)
    

@koi_net_router.post(POLL_EVENTS_PATH)
async def poll_events(req: PollEvents) -> EventsPayload:
    logger.info(f"Request to {POLL_EVENTS_PATH}")
    events = node.network.flush_poll_queue(req.rid)
    return EventsPayload(events=events)

@koi_net_router.post(FETCH_RIDS_PATH)
async def fetch_rids(req: FetchRids) -> RidsPayload:
    return node.network.response_handler.fetch_rids(req)

@koi_net_router.post(FETCH_MANIFESTS_PATH)
async def fetch_manifests(req: FetchManifests) -> ManifestsPayload:
    return node.network.response_handler.fetch_manifests(req)

@koi_net_router.post(FETCH_BUNDLES_PATH)
async def fetch_bundles(req: FetchBundles) -> BundlesPayload:
    bundles_payload = node.network.response_handler.fetch_bundles(req)
    return await fetch_missing(bundles_payload)

app.include_router(koi_net_router)