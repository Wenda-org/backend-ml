from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.routes import router as api_router


# ---------------------------------------------------------------------------
# Custom CORS fallback middleware
# Ensures Access-Control-Allow-Origin is ALWAYS present, even on error
# responses that slip past FastAPI's built-in CORSMiddleware.
# ---------------------------------------------------------------------------
class ForceCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Handle preflight OPTIONS requests immediately
        if request.method == "OPTIONS":
            response = JSONResponse(content={}, status_code=200)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-ML-API-KEY, Accept, Origin"
            )
            response.headers["Access-Control-Max-Age"] = "86400"
            return response

        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-ML-API-KEY, Accept, Origin"
        )
        return response


app = FastAPI(
    title="Wenda ML Backend",
    version="0.1.0",
    description="Backend de Machine Learning para a plataforma Wenda",
)

# Order matters: ForceCORSMiddleware runs first (outermost), CORSMiddleware second
app.add_middleware(ForceCORSMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"service": "wenda-ml-backend", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "wenda-ml-backend"}
