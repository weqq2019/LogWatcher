from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Category(Base):
    """分类表"""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, comment="分类名称")
    description = Column(Text, comment="分类描述")
    color = Column(String(7), default="#1890ff", comment="分类颜色")
    icon = Column(String(50), comment="分类图标")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    news_articles = relationship("NewsArticle", back_populates="category")
    tool_updates = relationship("ToolUpdate", back_populates="category")
    project_releases = relationship("ProjectRelease", back_populates="category")


class NewsArticle(Base):
    """技术新闻表"""

    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), index=True, comment="新闻标题")
    summary = Column(Text, comment="新闻摘要")
    content = Column(Text, comment="新闻内容")
    url = Column(String(1000), unique=True, index=True, comment="新闻链接")
    source = Column(String(100), index=True, comment="新闻来源")
    author = Column(String(100), comment="作者")
    published_at = Column(DateTime, index=True, comment="发布时间")
    tags = Column(JSON, comment="标签列表")
    category_id = Column(Integer, ForeignKey("categories.id"), comment="分类ID")
    read_count = Column(Integer, default=0, comment="阅读次数")
    is_featured = Column(Boolean, default=False, comment="是否推荐")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    category = relationship("Category", back_populates="news_articles")


class ToolUpdate(Base):
    """工具更新表"""

    __tablename__ = "tool_updates"

    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String(100), index=True, comment="工具名称")
    version = Column(String(50), comment="版本号")
    title = Column(String(500), comment="更新标题")
    description = Column(Text, comment="更新描述")
    changelog = Column(Text, comment="变更日志")
    url = Column(String(1000), comment="更新链接")
    download_url = Column(String(1000), comment="下载链接")
    release_notes = Column(Text, comment="发布说明")
    published_at = Column(DateTime, index=True, comment="发布时间")
    category_id = Column(Integer, ForeignKey("categories.id"), comment="分类ID")
    tags = Column(JSON, comment="标签列表")
    is_major = Column(Boolean, default=False, comment="是否重大更新")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    category = relationship("Category", back_populates="tool_updates")


class ProjectRelease(Base):
    """项目发布表"""

    __tablename__ = "project_releases"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100), index=True, comment="项目名称")
    repo_url = Column(String(1000), comment="仓库地址")
    version = Column(String(50), comment="版本号")
    tag_name = Column(String(100), comment="标签名称")
    title = Column(String(500), comment="发布标题")
    description = Column(Text, comment="发布描述")
    changelog = Column(Text, comment="变更日志")
    published_at = Column(DateTime, index=True, comment="发布时间")
    category_id = Column(Integer, ForeignKey("categories.id"), comment="分类ID")
    language = Column(String(50), comment="主要编程语言")
    stars = Column(Integer, default=0, comment="Star数量")
    forks = Column(Integer, default=0, comment="Fork数量")
    is_prerelease = Column(Boolean, default=False, comment="是否预发布")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    category = relationship("Category", back_populates="project_releases")


class UserPreference(Base):
    """用户偏好设置表"""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, comment="用户ID")
    favorite_categories = Column(JSON, comment="关注的分类")
    favorite_tools = Column(JSON, comment="关注的工具")
    favorite_projects = Column(JSON, comment="关注的项目")
    notification_settings = Column(JSON, comment="通知设置")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CollectorLog(Base):
    """收集器日志表"""

    __tablename__ = "collector_logs"

    id = Column(Integer, primary_key=True, index=True)
    collector_name = Column(String(100), index=True, comment="收集器名称")
    status = Column(String(20), index=True, comment="执行状态")
    message = Column(Text, comment="执行信息")
    items_collected = Column(Integer, default=0, comment="收集条目数")
    execution_time = Column(Integer, comment="执行时间(秒)")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 状态常量
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_RUNNING = "running"
