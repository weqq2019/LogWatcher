from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class CursorUpdateBase(BaseModel):
    """Cursor 更新基础模型"""

    version: str = Field(..., description="版本号")
    release_date: datetime = Field(..., description="发布日期")
    title: str = Field(..., description="更新标题")
    translated_title: str = Field(..., description="中文翻译标题")
    original_content: str = Field(..., description="原始英文内容")
    translated_content: str = Field(..., description="中文翻译内容")
    analysis: str = Field(..., description="分析结果")
    url: str = Field(..., description="更新链接")
    collector: str = Field(default="cursor_collector", description="采集器名称")
    collected_at: datetime = Field(..., description="采集时间")
    is_major: bool = Field(default=False, description="是否重大更新")


class CursorUpdateResponse(CursorUpdateBase):
    """Cursor 更新响应模型"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CursorUpdateListResponse(BaseModel):
    """Cursor 更新列表响应模型"""

    updates: List[CursorUpdateResponse]
    total: int
    skip: int
    limit: int


class CursorUpdateCreate(CursorUpdateBase):
    """创建 Cursor 更新模型"""

    pass


class CursorUpdateUpdate(BaseModel):
    """更新 Cursor 更新模型"""

    title: Optional[str] = None
    original_content: Optional[str] = None
    translated_content: Optional[str] = None
    analysis: Optional[str] = None
    url: Optional[str] = None
    is_major: Optional[bool] = None
    is_active: Optional[bool] = None


# 通用响应模型
class MessageResponse(BaseModel):
    """通用消息响应模型"""

    success: bool
    message: str
    data: Optional[dict] = None


class CollectorResponse(BaseModel):
    """采集器响应模型"""

    success: bool
    message: str
    total_items: int
    saved_count: int


class CursorStatsResponse(BaseModel):
    """Cursor 统计响应模型"""

    total_updates: int
    major_updates: int
    latest_version: Optional[str]
    latest_release_date: Optional[datetime]
 