from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_tools():
    """获取工具更新列表"""
    # TODO #3 数据收集器: 实现工具更新列表接口
    return {"message": "工具更新接口待实现"}


@router.get("/{tool_id}")
async def get_tool(tool_id: int):
    """获取工具更新详情"""
    # TODO #3 数据收集器: 实现工具更新详情接口
    return {"message": f"工具更新详情接口待实现, ID: {tool_id}"}
