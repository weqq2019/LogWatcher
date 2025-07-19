# 🏗️ LogWatcher 项目目录结构

> **版本**: v1.1  
> **更新时间**: 2025-01-19  
> **维护**: Claude Code 自动生成

## 📁 项目根目录结构

```
LogWatcher/
├── .gitignore                       # Git忽略文件配置
├── CLAUDE.md                        # Claude Code工作指令
├── AI_COLLECT_CONFIG.md             # AI收集器配置说明
├── TODO.md                          # 项目待办任务
├── README.md                        # 项目说明文档
├── LogWatcher.code-workspace        # VSCode工作区配置
├── database_migration_add_model.sql # 数据库迁移脚本
├── docker-compose.yml               # Docker编排配置
├── test_docker_ai_news.py           # Docker环境测试脚本
├── backend/                         # 后端服务目录
├── frontend/                        # 前端应用目录
└── mermaid/                         # 架构图和流程图
```

## 🎯 后端目录结构 (backend/)

```
backend/
├── main.py                          # FastAPI应用主入口
├── config.py                        # 应用配置管理
├── database.py                      # 数据库连接和会话
├── models.py                        # SQLAlchemy数据模型
├── schemas.py                       # Pydantic请求/响应模型
├── websocket_manager.py             # WebSocket连接管理
├── simple_routes.py                 # 简单路由定义
├── requirements.txt                 # Python依赖清单
├── Dockerfile                       # 后端Docker构建文件
├── README_parser.md                 # 解析器说明文档
├── routes/                          # API路由模块
│   ├── __init__.py                  # 路由模块初始化
│   ├── collectors.py                # 收集器管理API
│   ├── cursor.py                    # Cursor工具相关API
│   ├── dashboard.py                 # 仪表盘数据API
│   ├── news.py                      # 新闻数据API
│   ├── projects.py                  # 项目发布API
│   └── tools.py                     # 工具更新API
├── collectors/                      # 数据收集器模块
│   ├── __init__.py                  # 收集器模块初始化
│   ├── base.py                      # 基础收集器抽象类
│   ├── manager.py                   # 收集器管理器
│   ├── ai_news_collector.py         # AI新闻收集器
│   └── cursor_collector.py          # Cursor更新收集器
└── 测试文件集合/
    ├── quick_test.py                # 快速功能测试
    ├── test_collector.py            # 收集器基础测试
    ├── test_collector_local.py      # 本地收集器测试
    ├── test_ai_news.py              # AI新闻收集器测试
    ├── test_ai_news_debug.py        # AI新闻调试测试
    ├── test_ai_news_internal.py     # AI新闻内部测试
    ├── test_ai_news_quick.py        # AI新闻快速测试
    ├── test_network.py              # 网络连接测试
    ├── test_ip_direct.py            # IP直连测试
    ├── test_official_api.py         # 官方API测试
    ├── test_socks_bypass.py         # SOCKS代理测试
    ├── test_api_response.txt         # API响应测试数据
    ├── debug_cursor_network.py      # Cursor网络调试
    └── debug_cursor_response.html    # Cursor响应调试
```

## 🖼️ 前端目录结构 (frontend/)

```
frontend/
├── package.json                     # npm依赖和脚本配置
├── package-lock.json                # 依赖版本锁定文件
├── vite.config.js                   # Vite构建工具配置
├── index.html                       # 应用入口HTML文件
├── Dockerfile                       # 前端Docker构建文件
├── nginx.conf                       # Nginx服务器配置
├── node_modules/                    # npm安装的依赖包
└── src/                             # 前端源代码目录
    ├── App.vue                      # Vue根组件
    ├── main.js                      # 应用初始化入口
    ├── components/                  # 可复用组件目录
    │   └── NewsList.vue             # 新闻列表组件
    ├── views/                       # 页面组件目录
    │   ├── Dashboard.vue            # 仪表盘页面
    │   ├── News.vue                 # 新闻页面
    │   ├── Tools.vue                # 工具页面
    │   ├── Projects.vue             # 项目页面
    │   └── Cursor.vue               # Cursor页面
    └── router/                      # 路由配置目录
        └── index.js                 # Vue Router路由配置
```

## 📊 架构图目录结构 (mermaid/)

```
mermaid/
├── LogWatcher系统整体架构流程.mmd         # 系统整体架构图
├── AI新闻收集完整流程.mmd               # AI新闻收集完整流程
├── AI新闻收集技术架构.mmd               # AI新闻收集技术架构
├── AI新闻收集核心流程.mmd               # AI新闻收集核心流程
├── Cursor采集器API调用流程.mmd          # Cursor采集器API调用流程
├── Cursor采集器主要流程.mmd             # Cursor采集器主要流程
├── Cursor采集器数据库优化.mmd           # Cursor采集器数据库优化
├── Cursor采集器解析策略.mmd             # Cursor采集器解析策略
├── Cursor采集器进度显示.mmd             # Cursor采集器进度显示
└── DeepSeek AI分析功能模块图.png        # DeepSeek AI分析功能模块图
```

---

## 📋 结构变更记录

### v1.1 (2025-01-19)
**配置优化：**
- ✅ `CLAUDE.md` - 强制要求Git提交包含issue编号，养成规范提交习惯
- ✅ `structure.md` - 新增结构变更记录模块，便于追踪项目演进

**规范完善：**
- Git提交模板：移除可选标记，issue编号改为必填项
- 特殊情况处理：定义通用issue编号规则 (#1文档, #2配置, #3功能, #4修复)