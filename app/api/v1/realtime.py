from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.events import RealtimeState

router = APIRouter()


@router.websocket("/ws/live-state")
async def live_state_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        await websocket.send_json(RealtimeState().model_dump())
        while True:
            payload = await websocket.receive_text()
            await websocket.send_text(payload)
    except WebSocketDisconnect:
        return
