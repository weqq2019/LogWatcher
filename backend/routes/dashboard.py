from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_dashboard():
    """获取仪表盘数据"""
    # TODO #3 数据收集器: 实现仪表盘数据接口
    return {"message": "仪表盘接口待实现"}


@router.get("/stats")
async def get_dashboard_stats():
    """获取统计信息"""
    # TODO #3 数据收集器: 实现统计信息接口
    return {"message": "统计信息接口待实现"}
