from fastapi import FastAPI
from routes.api import router as api_router

app = FastAPI(title="Bach AI Control API", version="1.1.0")

# Register main API router
app.include_router(api_router)
