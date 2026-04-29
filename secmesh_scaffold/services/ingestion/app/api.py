from __future__ import annotations

import uuid
from fastapi import APIRouter
from secmesh_common.models import EvidenceEvent

router = APIRouter(prefix="/v1")

@router.post("/ingest")
def ingest(event: EvidenceEvent):
    # Scaffold: store to an append-only evidence store and publish to a queue for normalization.
    return {"accepted": True, "received_event_id": event.event_id, "ingestion_id": str(uuid.uuid4())}
