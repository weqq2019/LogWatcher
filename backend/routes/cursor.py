from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import CursorUpdate
from schemas import CursorUpdateResponse, CursorUpdateListResponse
from collectors.cursor_collector import CursorCollector

router = APIRouter(prefix="/cursor", tags=["cursor"])


@router.get("/updates", response_model=CursorUpdateListResponse)
async def get_cursor_updates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取 Cursor 更新日志列表"""
    query = db.query(CursorUpdate).filter(CursorUpdate.is_active == True)

    total = query.count()
    updates = (
        query.order_by(CursorUpdate.release_date.desc()).offset(skip).limit(limit).all()
    )

    return CursorUpdateListResponse(
        updates=updates, total=total, skip=skip, limit=limit
    )


@router.get("/updates/{version}", response_model=CursorUpdateResponse)
async def get_cursor_update(version: str, db: Session = Depends(get_db)):
    """获取特定版本的 Cursor 更新详情"""
    update = (
        db.query(CursorUpdate)
        .filter(CursorUpdate.version == version, CursorUpdate.is_active == True)
        .first()
    )

    if not update:
        raise HTTPException(status_code=404, detail="更新版本不存在")

    return CursorUpdateResponse.from_orm(update)


@router.get("/updates/latest", response_model=CursorUpdateResponse)
async def get_latest_cursor_update(db: Session = Depends(get_db)):
    """获取最新的 Cursor 更新"""
    update = (
        db.query(CursorUpdate)
        .filter(CursorUpdate.is_active == True)
        .order_by(CursorUpdate.release_date.desc())
        .first()
    )

    if not update:
        raise HTTPException(status_code=404, detail="暂无更新数据")

    return CursorUpdateResponse.from_orm(update)


@router.post("/collect")
async def collect_cursor_updates(db: Session = Depends(get_db)):
    """手动触发 Cursor 更新日志采集"""
    try:
        collector = CursorCollector()

        # 设置数据库会话，让采集器能够检查版本是否已存在
        collector.db_session = db

        items = await collector.collect()

        saved_count = 0
        updated_count = 0
        collection_info = {}

        # 获取采集信息
        if items and "collection_info" in items[0].extra_data:
            collection_info = items[0].extra_data["collection_info"]

        for item in items:
            # 检查是否已存在
            existing = (
                db.query(CursorUpdate)
                .filter(CursorUpdate.version == item.extra_data.get("version", ""))
                .first()
            )

            if existing:
                # 更新现有记录
                existing.title = item.title
                existing.translated_title = item.extra_data.get("translated_title", "")
                existing.original_content = item.extra_data.get("original_content", "")
                existing.translated_content = item.extra_data.get(
                    "translated_content", ""
                )
                existing.analysis = item.extra_data.get("analysis", "")
                existing.url = item.url
                existing.collected_at = datetime.utcnow()
                existing.updated_at = datetime.utcnow()
                if item.extra_data.get("collection_status") == "new":
                    updated_count += 1
            else:
                # 创建新记录
                cursor_update = CursorUpdate(
                    version=item.extra_data.get("version", ""),
                    release_date=item.published_at or datetime.utcnow(),
                    title=item.title,
                    translated_title=item.extra_data.get("translated_title", ""),
                    original_content=item.extra_data.get("original_content", ""),
                    translated_content=item.extra_data.get("translated_content", ""),
                    analysis=item.extra_data.get("analysis", ""),
                    url=item.url,
                    collected_at=datetime.utcnow(),
                    is_major=item.extra_data.get("is_major", False),
                )
                db.add(cursor_update)
                saved_count += 1

        db.commit()

        return {
            "success": True,
            "message": f"采集完成！共处理 {len(items)} 个版本，新增 {saved_count} 个，更新 {updated_count} 个",
            "total_items": len(items),
            "saved_count": saved_count,
            "updated_count": updated_count,
            "collection_info": {
                "total_versions": collection_info.get("total_versions", 0),
                "new_versions": collection_info.get("new_versions", 0),
                "existing_versions": collection_info.get("existing_versions", 0),
                "api_calls_made": collection_info.get("api_calls_made", 0),
                "processing_details": collection_info.get("processing_details", []),
            },
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"采集失败: {str(e)}")


@router.get("/stats")
async def get_cursor_stats(db: Session = Depends(get_db)):
    """获取 Cursor 更新统计信息"""
    total_updates = (
        db.query(CursorUpdate).filter(CursorUpdate.is_active == True).count()
    )
    major_updates = (
        db.query(CursorUpdate)
        .filter(CursorUpdate.is_active == True, CursorUpdate.is_major == True)
        .count()
    )

    latest_update = (
        db.query(CursorUpdate)
        .filter(CursorUpdate.is_active == True)
        .order_by(CursorUpdate.release_date.desc())
        .first()
    )

    return {
        "total_updates": total_updates,
        "major_updates": major_updates,
        "latest_version": latest_update.version if latest_update else None,
        "latest_release_date": latest_update.release_date if latest_update else None,
    }
