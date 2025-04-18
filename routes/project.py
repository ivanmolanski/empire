from fastapi import APIRouter, status, Path
from models import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectListResponse,
    ErrorResponse
)

router = APIRouter()

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project"
)
def create_project(request: ProjectCreateRequest):
    """
    Create a new project for the current user.
    - **name**: Project name.
    - **description**: Project description.
    """
    # TODO: Add database logic to create project.
    return ProjectResponse(project_id="proj_123", name=request.name, description=request.description)

@router.get(
    "",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all projects for the current user"
)
def list_projects():
    """
    List all projects for the authenticated user.
    """
    # TODO: Query database for user's projects.
    return ProjectListResponse(projects=[])

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    responses={404: {"model": ErrorResponse}},
    status_code=status.HTTP_200_OK,
    summary="Get project details"
)
def get_project(project_id: str = Path(..., description="Project identifier")):
    """
    Get details for a specific project.
    """
    # TODO: Query database for project details.
    return ProjectResponse(project_id=project_id, name="Example Project", description="A sample project.")

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project"
)
def delete_project(project_id: str = Path(..., description="Project identifier")):
    """
    Delete a specific project.
    """
    # TODO: Delete project from database.
    return
