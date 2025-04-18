from fastapi import APIRouter, status, Query
from app.models import TaskStatusResponse, ErrorResponse

router = APIRouter()

@router.get(
    "/status",
    response_model=TaskStatusResponse,
    responses={404: {"model": ErrorResponse}},
    status_code=status.HTTP_200_OK,
    summary="Get the status of a background task"
)
def get_task_status(task_id: str = Query(..., description="Task identifier")):
    """
    Get the status and result of a background task.
    - **task_id**: The unique identifier of the background task.
    """
    # TODO: Query task status from database or task queue.
    return TaskStatusResponse(task_id=task_id, status="completed", result="Task finished successfully.")
