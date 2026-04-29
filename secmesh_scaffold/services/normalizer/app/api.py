from __future__ import annotations

from fastapi import APIRouter
from secmesh_common.models import EvidenceEvent

router = APIRouter(prefix="/v1")

@router.post("/normalize")
def normalize(event: EvidenceEvent):
    # Scaffold: validate + normalize into typed objects and store in graph
    return {
        "event_id": event.event_id,
        "asset": event.asset.model_dump(),
        "event_type": event.event_type,
        "normalized_payload_keys": sorted(list(event.payload.keys())),
        "context_keys": sorted(list(event.context.keys())),
    }
