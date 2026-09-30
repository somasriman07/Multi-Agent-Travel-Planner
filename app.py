from pathlib import Path
import traceback
import mimetypes
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend import run_travel_agent

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="TripMate AI",
    description="LangGraph Multi-Agent Travel Planner with FastAPI Frontend",
    version="1.0.0"
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@app.get("/static/{filename:path}")
async def static_files(filename: str):
    """Serve static files by reading content directly — avoids anyio thread issues."""
    file_path = STATIC_DIR / filename
    # Resolve and guard against path traversal
    try:
        file_path = file_path.resolve()
        STATIC_DIR.resolve()
        if not str(file_path).startswith(str(STATIC_DIR.resolve())):
            return Response(status_code=403)
    except Exception:
        return Response(status_code=400)

    if not file_path.exists() or not file_path.is_file():
        return Response(status_code=404)

    media_type, _ = mimetypes.guess_type(str(file_path))
    content = file_path.read_bytes()
    return Response(
        content=content,
        media_type=media_type or "application/octet-stream"
    )



class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/api/travel")
async def travel_planner(request_data: TravelRequest):
    try:
        user_message = request_data.message.strip()

        if not user_message:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty."
                }
            )

        result = await run_travel_agent(
            user_input=user_message,
            thread_id=request_data.thread_id
        )

        return JSONResponse(
            content={
                "success": True,
                "thread_id": result["thread_id"],
                "answer": result["answer"],
                "flight_results": result["flight_results"],
                "hotel_results": result["hotel_results"],
                "itinerary": result["itinerary"],
                "llm_calls": result["llm_calls"],
            }
        )

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )



@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "AI Travel Planner API is running"
    }


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={})



if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )