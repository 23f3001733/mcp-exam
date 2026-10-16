import hashlib
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

EMAIL = "23f3001733@ds.study.iitm.ac.in".strip().lower()

app = FastAPI()

TOOL = {
    "name": "solve_challenge",
    "description": "Returns the exam answer for the current request's challenge header.",
    "inputSchema": {"type": "object", "properties": {}},
}


def ok(msg_id, result):
    return JSONResponse({"jsonrpc": "2.0", "id": msg_id, "result": result})


def err(msg_id, code, message):
    return JSONResponse({"jsonrpc": "2.0", "id": msg_id,
                         "error": {"code": code, "message": message}})


@app.get("/")
async def health():
    return {"status": "alive"}


@app.post("/")
@app.post("/mcp")
async def mcp(request: Request):
    body = await request.json()
    method = body.get("method")
    msg_id = body.get("id")
    params = body.get("params") or {}

    # Notifications have no "id" and expect no reply body
    if msg_id is None:
        return Response(status_code=202)

    if method == "initialize":
        return ok(msg_id, {
            "protocolVersion": params.get("protocolVersion", "2025-03-26"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "exam-server", "version": "1.0.0"},
        })

    if method == "ping":
        return ok(msg_id, {})

    if method == "tools/list":
        return ok(msg_id, {"tools": [TOOL]})

    if method == "tools/call":
        if params.get("name") != "solve_challenge":
            return err(msg_id, -32602, "Unknown tool")
        # Read the challenge from the HTTP HEADER, not the JSON body
        challenge = request.headers.get("x-exam-challenge", "")
        answer = hashlib.sha256(f"{challenge}:{EMAIL}".encode()).hexdigest()[:16]
        return ok(msg_id, {"content": [{"type": "text", "text": answer}]})

    return err(msg_id, -32601, f"Method not found: {method}")
