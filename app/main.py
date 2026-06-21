from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.routes import router as api_router


# ---------------------------------------------------------------------------
# Manual CORS middleware — handles ALL cases including errors and 4xx/5xx.
# We do NOT use FastAPI's CORSMiddleware because it can return 400 on
# preflight if the route doesn't exist yet, blocking the browser.
# ---------------------------------------------------------------------------

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": (
        "Content-Type, Authorization, X-ML-API-KEY, "
        "Accept, Origin, X-Requested-With"
    ),
    "Access-Control-Max-Age": "86400",
}


class CORSMiddleware(BaseHTTPMiddleware):
    """Injects CORS headers on every response, handles OPTIONS preflights."""

    async def dispatch(self, request: Request, call_next):
        # Immediately handle OPTIONS preflight — no further processing needed
        if request.method == "OPTIONS":
            resp = Response(status_code=200, content="")
            for k, v in CORS_HEADERS.items():
                resp.headers[k] = v
            return resp

        # For all other methods, proceed normally and inject CORS headers
        response = await call_next(request)
        for k, v in CORS_HEADERS.items():
            response.headers[k] = v
        return response


app = FastAPI(
    title="Wenda ML Backend",
    version="0.1.0",
    description="Backend de Machine Learning para a plataforma Wenda",
)

# Single custom CORS middleware — handles everything
app.add_middleware(CORSMiddleware)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"service": "wenda-ml-backend", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "wenda-ml-backend"}
