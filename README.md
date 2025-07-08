# LogWatcher - 每日技术雷达

## 📡 项目简介

LogWatcher 是一个自动化技术雷达系统，帮助开发者追踪：
- 🔥 技术新闻和行业动态
- 🛠️ 工具更新日志 (GPT、Cursor、GitHub等)
- 📦 开源项目发布动态
- 🎯 个性化技术关注点

## 🏗️ 技术栈

### 后端
- **FastAPI** - 高性能Python Web框架
- **MySQL** - 关系型数据库
- **SQLAlchemy** - ORM框架
- **APScheduler** - 定时任务调度

### 前端
- **Vue3** - 渐进式JavaScript框架
- **Composition API** - 组合式API
- **Pinia** - 状态管理
- **Element Plus** - UI组件库

### 数据收集
- **requests** - HTTP请求库
- **BeautifulSoup** - HTML解析
- **feedparser** - RSS订阅解析
- **GitHub API** - 开源项目追踪

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Docker (可选)

### 启动步骤
```bash
# 1. 克隆项目
git clone <your-repo>
cd LogWatcher

# 2. 启动后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 3. 启动前端
cd frontend
npm install
npm run dev
```

## 📊 功能特性

- 🔄 自动数据收集与更新
- 📱 响应式技术雷达界面
- 🔍 智能搜索与过滤
- 📈 趋势分析与统计
- 🎨 美观的现代化UI

## 🗂️ 项目结构

```
LogWatcher/
├── backend/          # FastAPI后端
├── frontend/         # Vue3前端
├── collectors/       # 数据收集器
├── docker-compose.yml
└── README.md
```

## 🔧 配置说明

环境变量配置请参考 `.env.example` 文件。

## �� 许可证

MIT License 