from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

app = FastAPI(title="Wenda ML Backend", version="0.1.0")

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "https://backend-ml-c75p.onrender.com", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"service": "wenda-ml-backend", "status": "ok"}
