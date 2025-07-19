from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_collectors():
    return {"message": "收集器列表"}


@router.post("/run/{collector_name}")
async def run_collector(collector_name: str):
    return {"message": f"运行收集器 {collector_name}"}
