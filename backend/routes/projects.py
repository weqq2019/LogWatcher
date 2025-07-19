from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_projects():
    return {"message": "项目列表"}


@router.get("/{project_id}")
async def get_project_detail(project_id: int):
    return {"message": f"项目详情 {project_id}"}
