from fastapi import APIRouter, HTTPException, Path
from models import ProjectCreateRequest, ProjectResponse, ProjectListResponse

router = APIRouter()

@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(project: ProjectCreateRequest):
    # TODO: Add DB logic
    return ProjectResponse(project_id="proj_001", name=project.name, description=project.description)

@router.get("", response_model=ProjectListResponse)
def list_projects():
    return ProjectListResponse(projects=[
        ProjectResponse(project_id="proj_001", name="Project 1", description="First project")
    ])

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str = Path(...)):
    return ProjectResponse(project_id=project_id, name="Example Project", description="A project")

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str = Path(...)):
    # TODO: Delete project from DB
    return