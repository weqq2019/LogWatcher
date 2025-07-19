from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import uuid
import asyncio

from database import create_tables, engine
from routes import news, tools, projects, dashboard, collectors, cursor
from websocket_manager import websocket_manager


# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    create_tables()
    yield
    # 关闭时清理资源
    engine.dispose()


# 创建FastAPI应用
app = FastAPI(
    title="LogWatcher API",
    description="每日技术雷达 - 自动追踪技术新闻和工具更新",
    version="1.0.0",
    lifespan=lifespan,
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vue3开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "LogWatcher API is running"}


# WebSocket路由
@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    """WebSocket端点 - 支持实时通信"""
    connection_id = str(uuid.uuid4())

    if await websocket_manager.connect(websocket, connection_id, room):
        try:
            # 保持连接活跃
            while True:
                # 等待客户端消息
                data = await websocket.receive_text()

                # 处理客户端消息（如果需要）
                # 这里可以添加消息处理逻辑

                # 发送心跳响应
                await websocket_manager.send_personal_message(
                    connection_id,
                    {
                        "type": "heartbeat",
                        "message": "pong",
                        "timestamp": asyncio.get_event_loop().time(),
                    },
                )

        except WebSocketDisconnect:
            websocket_manager.disconnect(connection_id)
        except Exception as e:
            print(f"WebSocket错误: {e}")
            websocket_manager.disconnect(connection_id)
    else:
        await websocket.close(code=1000, reason="连接建立失败")


# 获取WebSocket状态
@app.get("/api/v1/websocket/status")
async def get_websocket_status():
    """获取WebSocket连接状态"""
    return {
        "total_connections": websocket_manager.get_total_connections(),
        "rooms": {
            room: len(connections)
            for room, connections in websocket_manager.rooms.items()
        },
    }


# 注册路由
app.include_router(news.router, prefix="/api/v1/news", tags=["技术新闻"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["工具更新"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["开源项目"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["仪表盘"])
app.include_router(collectors.router, prefix="/api/v1/collectors", tags=["数据收集器"])
app.include_router(cursor.router, prefix="/api/v1", tags=["Cursor更新"])


# 根路径
@app.get("/")
async def root():
    return {
        "message": "欢迎使用 LogWatcher 技术雷达 API",
        "docs": "/docs",
        "version": "1.0.0",
        "websocket": "ws://localhost:8000/ws/{room}",
    }


# 错误处理
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500, content={"detail": f"服务器内部错误: {str(exc)}"}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
