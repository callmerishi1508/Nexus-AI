import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.event_stream import event_bus

router = APIRouter()

@router.get("/stream")
async def event_stream(tenant_id: str = "tenant_public"):
    async def event_generator():
        queue = await event_bus.subscribe()
        try:
            while True:
                message = await queue.get()
                # Optional: filter by tenant_id if event has it
                if message.get("tenant_id", tenant_id) == tenant_id:
                    yield f"data: {json.dumps(message['payload'])}\n\n"
        except asyncio.CancelledError:
            event_bus.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
