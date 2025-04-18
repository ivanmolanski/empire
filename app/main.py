from fastapi import FastAPI
from app.routes.api import router as api_router
from app.config import settings

app = FastAPI(title="Bach AI Empire API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}

app.include_router(api_router)
