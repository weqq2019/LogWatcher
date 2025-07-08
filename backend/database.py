from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/logwatcher"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DATABASE_ECHO", "False").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """获取数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """上下文管理器方式获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """创建所有数据库表"""
    from models import NewsArticle, ToolUpdate, ProjectRelease, Category

    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")


def drop_tables():
    """删除所有数据库表"""
    Base.metadata.drop_all(bind=engine)
    print("❌ 数据库表删除完成")


# 数据库连接测试
def test_connection():
    """测试数据库连接"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ 数据库连接成功")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


if __name__ == "__main__":
    test_connection()
