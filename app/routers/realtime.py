import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/api/realtime", tags=["realtime"])

# Global event queue for broadcasting messages to all connected clients on the selection page.
# In a real distributed system, we would use Redis Pub/Sub, but for SQLite/FastAPI local, this works.
clients = []

async def broadcast_event(data: str):
    for queue in clients:
        await queue.put(data)

@router.get("/stream")
async def message_stream(request: Request):
    queue = asyncio.Queue()
    clients.append(queue)
    
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                data = await queue.get()
                yield {
                    "event": "update",
                    "data": data
                }
        except asyncio.CancelledError:
            pass
        finally:
            clients.remove(queue)
            
    return EventSourceResponse(event_generator())
