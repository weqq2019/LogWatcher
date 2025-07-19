from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Any, Optional
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 活动的WebSocket连接 {connection_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # 按房间分组的连接 {room: {connection_id}}
        self.rooms: Dict[str, Set[str]] = {}

    async def connect(
        self, websocket: WebSocket, connection_id: str, room: str = "default"
    ) -> bool:
        """建立WebSocket连接"""
        try:
            await websocket.accept()
            self.active_connections[connection_id] = websocket

            # 加入房间
            if room not in self.rooms:
                self.rooms[room] = set()
            self.rooms[room].add(connection_id)

            logger.info(f"WebSocket连接建立: {connection_id} 加入房间 {room}")

            # 发送连接确认消息
            await self.send_personal_message(
                connection_id,
                {
                    "type": "connection_established",
                    "connection_id": connection_id,
                    "room": room,
                    "timestamp": asyncio.get_event_loop().time(),
                },
            )

            return True

        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            return False

    def disconnect(self, connection_id: str):
        """断开WebSocket连接"""
        if connection_id in self.active_connections:
            # 从所有房间中移除
            for room, connections in self.rooms.items():
                connections.discard(connection_id)

            # 移除连接
            del self.active_connections[connection_id]
            logger.info(f"WebSocket连接断开: {connection_id}")

    async def send_personal_message(self, connection_id: str, message: Dict[str, Any]):
        """向特定连接发送消息"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except WebSocketDisconnect:
                self.disconnect(connection_id)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                self.disconnect(connection_id)

    async def broadcast_to_room(self, room: str, message: Dict[str, Any]):
        """向房间中的所有连接广播消息"""
        if room in self.rooms:
            disconnected_connections = []

            for connection_id in self.rooms[room]:
                if connection_id in self.active_connections:
                    websocket = self.active_connections[connection_id]
                    try:
                        await websocket.send_text(
                            json.dumps(message, ensure_ascii=False)
                        )
                    except WebSocketDisconnect:
                        disconnected_connections.append(connection_id)
                    except Exception as e:
                        logger.error(f"广播消息失败: {e}")
                        disconnected_connections.append(connection_id)

            # 清理断开的连接
            for connection_id in disconnected_connections:
                self.disconnect(connection_id)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """向所有连接广播消息"""
        disconnected_connections = []

        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except WebSocketDisconnect:
                disconnected_connections.append(connection_id)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected_connections.append(connection_id)

        # 清理断开的连接
        for connection_id in disconnected_connections:
            self.disconnect(connection_id)

    def get_room_connections(self, room: str) -> Set[str]:
        """获取房间中的连接数"""
        return self.rooms.get(room, set())

    def get_total_connections(self) -> int:
        """获取总连接数"""
        return len(self.active_connections)


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()


class ProgressReporter:
    """进度报告器 - 用于在采集过程中发送实时进度"""

    def __init__(self, room: str = "cursor_collection"):
        self.room = room
        self.manager = websocket_manager

    async def report_progress(
        self, current: int, total: int, message: str, extra_data: Optional[Dict] = None
    ):
        """报告进度"""
        progress_data = {
            "type": "progress_update",
            "current": current,
            "total": total,
            "percentage": round((current / total) * 100, 1) if total > 0 else 0,
            "message": message,
            "timestamp": asyncio.get_event_loop().time(),
            "extra_data": extra_data or {},
        }

        await self.manager.broadcast_to_room(self.room, progress_data)

    async def report_status(
        self, status: str, message: str, data: Optional[Dict] = None
    ):
        """报告状态"""
        status_data = {
            "type": "status_update",
            "status": status,  # "started", "processing", "completed", "error"
            "message": message,
            "timestamp": asyncio.get_event_loop().time(),
            "data": data or {},
        }

        await self.manager.broadcast_to_room(self.room, status_data)

    async def report_version_progress(
        self,
        version: str,
        status: str,
        message: str,
        api_calls: int = 0,
        processing_time: float = 0,
    ):
        """报告版本处理进度"""
        version_data = {
            "type": "version_update",
            "version": version,
            "status": status,  # "processing", "completed", "skipped", "error"
            "message": message,
            "api_calls": api_calls,
            "processing_time": processing_time,
            "timestamp": asyncio.get_event_loop().time(),
        }

        await self.manager.broadcast_to_room(self.room, version_data)

    async def report_stats(self, stats: Dict):
        """报告统计信息"""
        stats_data = {
            "type": "stats_update",
            "stats": stats,
            "timestamp": asyncio.get_event_loop().time(),
        }

        await self.manager.broadcast_to_room(self.room, stats_data)
