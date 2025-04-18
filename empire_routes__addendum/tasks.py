from fastapi import APIRouter, HTTPException, Query
from models import TaskStatusResponse

router = APIRouter()

@router.get("/status", response_model=TaskStatusResponse)
def get_task_status(task_id: str = Query(...)):
    return TaskStatusResponse(task_id=task_id, status="completed", result="Task result placeholder")