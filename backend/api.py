import asyncio
import json
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from graph import app as graph_app
from schema import Market

load_dotenv()

api = FastAPI(title="Fintech Intel Squad API")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunRequest(BaseModel):
    query: str
    market: Market

class ReviewRequest(BaseModel):
    feedback: str


async def stream_graph(initial_state, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    gen = graph_app.astream(initial_state, config=config, stream_mode="updates")

    try:
        async for event in gen:
            if "__interrupt__" in event:
                interrupt_data = event["__interrupt__"][0].value
                notes = interrupt_data.get("skeptic_notes") or []
                if isinstance(notes, str):
                    notes = [notes]
                payload = {
                    "type":          "interrupt",
                    "message":       interrupt_data.get("message", ""),
                    "iteration":     interrupt_data.get("iteration", 0),
                    "skeptic_notes": notes,
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await gen.aclose()
                await asyncio.sleep(0.2)  # ✅ let checkpoint flush
                return

            for node_name, output in event.items():
                if node_name == "scout":
                    payload = {
                        "type":  "scout",
                        "count": len(output.get("raw_research_notes", [])),
                    }
                    yield f"data: {json.dumps(payload)}\n\n"

                elif node_name == "skeptic":
                    payload = {
                        "type":              "skeptic",
                        "is_satisfactory":   output.get("is_satisfactory", False),
                        "follow_up_queries": output.get("follow_up_queries", []),
                        "skeptic_notes":     output.get("skeptic_notes", []),
                    }
                    yield f"data: {json.dumps(payload)}\n\n"

                elif node_name == "writer":
                    brief = output.get("final_brief")
                    if brief:
                        payload = {
                            "type": "brief",
                            "data": brief.model_dump(),
                        }
                        yield f"data: {json.dumps(payload)}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        # ✅ surface errors to the client instead of silently 404ing
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    finally:
        await gen.aclose()

@api.post("/run")
async def run(request: RunRequest):
    """
    Initialise a new research session.
    Returns a thread_id the client uses for all subsequent calls.
    """

    thread_id = f"intel-{uuid.uuid4().hex[:8]}"
    return {"thread_id": thread_id, "query": request.query, "market": request.market}

@api.get("/stream/{thread_id}")
async def stream(thread_id: str, query: str, market: str):
    """
    SSE endpoint — streams agent events for a fresh run.
    Client connects here after receiving thread_id from /run.
    """
    initial_state = {
        "query":              query,
        "target_market":      market,
        "raw_research_notes": [],
        "iteration_count":    0,
        "is_satisfactory":    False,
        "follow_up_queries":  [],
        "final_brief":        None,
        "human_verdict":      None,
        "human_feedback":     None,
    }

    return StreamingResponse(
        stream_graph(initial_state, thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no", 
        },
    )
@api.post("/review/{thread_id}")
async def review(thread_id: str, request: ReviewRequest):
    config = {"configurable": {"thread_id": thread_id}}

    feedback = request.feedback.strip()
    first_word = feedback.split()[0].lower() if feedback else "reject"

    if first_word == "approve":
        human_verdict  = "approve"
        follow_up_queries = []

    elif first_word == "reject":
        human_verdict = "reject"
        remaining = " ".join(feedback.split()[1:]).strip()
        follow_up_queries = [remaining] if remaining else []
 

    else:
       
        human_verdict     = "comment"
        follow_up_queries = [feedback]

    graph_app.update_state(
        config,
        {
            "human_verdict":     human_verdict,
            "human_feedback":    feedback,
            "follow_up_queries": follow_up_queries,
        },
        as_node="human_review"
    )

    return {"status": "ok", "verdict": human_verdict}

@api.get("/resume/{thread_id}")
async def resume(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = graph_app.get_state(config)
    if not state or not state.values:
        raise HTTPException(status_code=404, detail=f"No checkpoint found for thread {thread_id}")

    return StreamingResponse(
        stream_graph(None, thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
