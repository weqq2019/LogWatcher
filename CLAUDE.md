# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# 📋 文档目录

1. [💬 技术表达优化指令](#技术表达优化指令)
2. [🏗️ 多语言项目结构规范](#多语言项目结构规范)
3. [🚀 Git 自动化工作流](#git-自动化工作流)
4. [📊 项目架构概览](#项目架构概览)

---

# 💬 技术表达优化指令

在回复用户时，请遵循以下格式：

1. **首先输出**：
   ```
   📝 **原始表达**：[用户的原始问题]
   ✨ **优化表达**：[技术上更准确、专业的表达方式]
   ```

2. **然后**：正常回答问题

## 优化目标
- 使用准确的技术术语
- 提供更清晰的问题描述
- 指出潜在的技术细节
- 建议更好的提问方式

## 示例
```
📝 **原始表达**：这些代码在容器运行 是不是我要重启容器?
✨ **优化表达**：修改了 Python 源代码后，由于容器内的应用进程已经加载了旧代码，是否需要重启容器来应用代码更改？
```

---

# 🏗️ 多语言项目结构规范

> 本文档指导 Claude Code 在本项目中的代码生成、结构组织与自动结构记录。  
> 本项目采用多语言架构（Python / Vue / TypeScript / Java / Go 等），需确保各模块职责清晰、结构一致、代码可维护、文档可追溯。

## 📚 规范目录

1. [📦 多语言模块结构标准](#多语言模块结构标准)
2. [🎯 单一职责原则 (SRP)](#单一职责原则-srp)
3. [📏 文件与函数复杂度控制](#文件与函数复杂度控制)
4. [🧠 命名与代码风格建议](#命名与代码风格建议)
5. [📚 自动结构记录结构](#自动结构记录结构)

---

## 📦 多语言模块结构标准

所有语言模块需统一遵循“**一目录一模块、一文件一职责**”的组织方式。Claude Code 应始终生成结构清晰、职责单一的代码。

### 🐍 Python 模块（FastAPI / Flask）

- `routes.py`：API 路由注册
- `service.py`：核心业务逻辑
- `schema.py`：请求/响应模型（Pydantic）
- `dao.py` / `crud.py`：数据库访问
- `utils.py`：本模块工具函数（非跨模块）

### 🖼 Vue / TypeScript 模块（Vue3）

- `XxxPage.vue`：页面组件（组合式 API）
- `composables/useXxx.ts`：逻辑封装（状态、计算）
- `api/xxxApi.ts`：接口请求封装
- `components/XxxItem.vue`：可复用 UI 子组件

### ☕ Java 模块（SpringBoot）

- `XxxController.java`：控制层
- `XxxService.java`：业务逻辑
- `XxxRepository.java`：数据访问层
- `XxxDto.java`：数据结构传输类

### 🌀 Go 模块

- `handler.go`：接口处理
- `service.go`：业务逻辑实现
- `model.go`：结构体定义
- `repo.go`：数据库封装

---

## 🎯 单一职责原则 (SRP)

Claude Code 必须遵循“单一职责原则”：

- 每个函数 / 文件 / 类仅完成一类任务
- 不允许在一个文件中混合视图逻辑、状态管理与数据库访问
- 若职责模糊或过多，必须主动建议拆分

📌 判断依据：

- 是否可单独测试？
- 是否会因多个原因变化？
- 是否影响模块复用？

---

## 📏 文件与函数复杂度控制

Claude Code 生成的代码必须控制在合理规模内，以下为推荐上限：

| 文件类型       | 推荐上限 | 强制上限 | 拆分建议                  |
|----------------|-----------|-----------|---------------------------|
| `.py` 文件     | ≤ 400 行  | < 500 行  | service / dao 拆分        |
| `.vue` 文件    | ≤ 400 行  | < 500 行  | 拆分 composables / 组件   |
| `.ts` / `.js`  | ≤ 400 行  | < 500 行  | 拆成 hooks / utils        |
| `.java`        | ≤ 500 行  | < 800 行  | 拆 controller/service/dto |
| `.go` 文件     | ≤ 500 行  | < 800 行  | 拆 handler / service 等   |

🔧 函数限制：

- 单个函数不超过 **30 行**
- 函数应聚焦一件事，避免嵌套层级超过 3 层

📌 所有行数包含注释、空行、import。结构复杂性 > 行数优先。

---

## 🧠 命名与代码风格建议

Claude Code 在生成文件与函数时，须遵循语言约定与语义清晰：

| 类型       | 命名风格     | 示例                   |
|------------|--------------|------------------------|
| Python     | `snake_case` | `get_user_info()`      |
| Java       | `PascalCase` | `UserController.java`  |
| Vue 组件   | `PascalCase` | `UserForm.vue`         |
| Composable | `useXxx`     | `useUserForm.ts`       |
| API 封装   | `xxxApi.ts`  | `userApi.ts`           |

📌 不得使用无意义命名如：`temp.js`、`test.py`、`final1.vue` 等。

---

## 📚 自动结构记录结构

### 🎯 更新触发条件
Claude Code 在执行以下操作时，**必须立即更新 `structure.md` 文件**：

#### 📁 文件系统变更
- 创建新目录或子目录（如 `[项目结构]/[子模块]/`）
- 创建新文件（任何扩展名：.py、.js、.vue、.java、.go、.rs 等）
- 删除或重命名重要文件/目录
- 移动文件到不同目录

#### 🔧 功能模块变更
- 新增 API/路由文件（根据项目技术栈）
- 新增业务逻辑模块（service、controller、handler 等）
- 新增页面/组件文件（React、Vue、Angular 等）
- 新增可复用组件或工具函数
- 新增数据模型、接口定义或类型声明
- 新增测试文件或测试套件

#### 🗄️ 数据存储变更
- 创建数据库迁移脚本（SQL、NoSQL、ORM）
- 新增或修改数据模型（任何ORM框架）
- 新增数据库初始化或种子脚本
- 新增配置文件（环境变量、配置类等）

### 📝 更新操作流程

1. **执行代码操作**：完成用户请求的文件创建/修改
2. **立即更新记录**：在同一回复中更新 structure.md
3. **版本递增**：每次更新时版本号 +0.1（如 v1.0 → v1.1）
4. **时间戳更新**：使用当前日期（格式：YYYY-MM-DD）

### 📦 详细记录格式

#### 版本信息更新（文件顶部）
```markdown
> **版本**: v1.2  
> **更新时间**: 2025-01-19  
> **维护**: Claude Code 自动生成
```

#### 结构变更记录（文件末尾追加）
```markdown
---

## 📋 结构变更记录

### v1.x (YYYY-MM-DD)
**新增模块：**
- ✅ `[目录路径]/[文件名.扩展名]` - [功能描述]
- ✅ `[相关目录]/[关联文件名]` - [关联功能说明]
- ✅ `[测试目录]/[测试文件名]` - [测试功能说明]

**目录调整：**
- 📁 新增 `[新目录路径]/` - [目录用途说明]
- 📁 重构 `[原目录]` → `[新目录]` - [重构原因]
- 📁 删除 `[废弃目录]/` - [删除原因]

**文件变更：**
- 🔄 重命名 `[原文件名]` → `[新文件名]` - [重命名原因]
- ➕ 新增 `[配置文件名]` - [配置用途]
- ➖ 删除 `[废弃文件名]` - [删除原因]

**功能说明：**
- [模块名称]：[具体功能描述和作用]
- [API/组件名]：[接口或组件的功能说明]
- [工具/脚本名]：[工具脚本的用途和使用方式]
```

### 🚨 重要执行规则

1. **立即性**：每次文件操作后立即更新，不得延迟或遗忘
2. **完整性**：记录所有相关文件变更，包括依赖文件的修改
3. **描述性**：每个文件都要有清晰的功能说明
4. **版本控制**：严格按版本号递增，便于追踪变更历史
5. **格式统一**：严格按照上述模板格式执行，保持文档一致性

---

# 🚀 Git 自动化工作流

## Git 环境预检查

在执行 Git 工作流之前，Claude 应该检查以下环境配置：

### 必要配置检查
```bash
# 1. 检查用户身份配置
git config user.name
git config user.email

# 2. 检查远程仓库连接
git remote -v

# 3. 检查当前分支状态
git status
git branch
```

### 预检查清单
- ✅ **用户身份**：确保已配置 `user.name` 和 `user.email`
- ✅ **远程仓库**：确保已连接到正确的远程仓库
- ✅ **分支状态**：确认当前在正确的分支上
- ✅ **工作区状态**：了解当前有哪些文件被修改
- ⚠️ **SSH/Token**：确保有推送权限（如需要 push）

### 配置缺失处理
1. **缺少用户配置**：提示用户先配置 Git 身份
2. **缺少远程仓库**：询问是否需要添加远程仓库
3. **权限问题**：提示检查 SSH 密钥或访问令牌

## 自动提交指令

当用户要求 Claude 进行代码修改后自动提交时，Claude 应该：

1. **完成代码修改**后，主动询问用户是否执行 Git 工作流
2. **等待用户确认**后，再执行 Git 命令序列
3. **使用标准化的提交消息格式**，包含 emoji 和 issue 编号

## Git 提交消息模板

使用以下格式的提交消息：
```
<emoji> <type>: <description> #issue-number

🚀 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**📌 重要**：issue编号为必填项，如果当前没有对应issue，请先创建一个。

### Emoji 映射规则
- 🚀 `feat` - 新功能
- 🐛 `fix` - 修复bug
- 📝 `docs` - 文档更新
- 💄 `style` - 代码格式化
- ♻️ `refactor` - 重构代码
- ⚡ `perf` - 性能优化
- ✅ `test` - 添加测试
- 🔧 `chore` - 构建配置
- 🗃️ `db` - 数据库相关
- 🔒 `security` - 安全相关

### 自动化命令序列
```bash
# 1. 添加所有更改
git add .

# 2. 使用模板提交
git commit -m "$(cat <<'EOF'
<emoji> <type>: <description> #issue-number

🚀 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# 3. 推送到远程（可选，根据用户需求）
git push
```

## 触发条件

当用户使用以下关键词时，Claude 应自动执行 Git 工作流：
- "提交代码"、"commit"
- "推送代码"、"push" 
- "自动提交"、"auto commit"
- "git 提交"

## 示例用法

用户：**"修改完数据收集器后自动提交代码 #12"**

Claude 执行流程：
1. 完成代码修改
2. **主动询问**：
   ```
   ✅ 代码修改完成！是否执行以下 Git 工作流？
   
   📋 预览操作：
   - git add .
   - git commit -m "♻️ refactor: 优化数据收集器架构和性能 #12"
   - git push（可选）
   
   请回复：yes/y 执行 | no/n 跳过 | push 执行并推送
   ```

**📌 特殊情况处理**：
- 如果用户未提供issue编号，Claude应提醒创建issue或使用通用issue编号
- 建议预设通用issue：#1(文档), #2(配置), #3(功能), #4(修复)
3. **等待用户确认**后执行相应操作
4. 使用标准化提交消息格式

## 确认响应选项

用户可以回复：
- **`yes` / `y`** - 执行 add + commit
- **`push` / `p`** - 执行 add + commit + push  
- **`no` / `n`** - 跳过所有 Git 操作
- **`preview`** - 仅显示将要执行的命令，不执行

---

# 📊 项目架构概览

LogWatcher 是一个全栈技术雷达系统，由以下主要组件构成：

- **后端 (FastAPI)**: 基于 Python 的 API 服务器，包含路由、数据模型、收集器和 WebSocket 支持
- **前端 (Vue3)**: 基于 Vue3 + Element Plus 的单页应用
- **数据收集器**: 模块化的数据收集系统，支持多种数据源（AI新闻、工具更新、项目发布）
- **数据库**: MySQL 8.0 用于数据存储，Redis 用于缓存
- **WebSocket**: 实时数据推送和状态更新

## 核心架构模式

### 数据收集器架构
所有收集器继承自 `BaseCollector` 类 (backend/collectors/base.py)，实现统一的 `collect()` 方法。收集器通过 `CollectorManager` 统一管理和调度。

### 路由组织
API 路由按功能模块组织：
- `/api/v1/news` - 技术新闻
- `/api/v1/tools` - 工具更新  
- `/api/v1/projects` - 开源项目
- `/api/v1/collectors` - 收集器管理
- `/api/v1/dashboard` - 仪表盘数据

### 数据模型
使用 SQLAlchemy ORM，主要模型包括：
- `NewsArticle` - 新闻文章
- `ToolUpdate` - 工具更新
- `ProjectRelease` - 项目发布
- `Category` - 分类管理

## 开发命令

### 后端开发
```bash
# 安装依赖
cd backend && pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 数据库操作
python database.py  # 测试数据库连接

# 测试收集器
python test_collector.py
python test_ai_news.py
```

### 前端开发
```bash
# 安装依赖
cd frontend && npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### Docker 部署
```bash
# 启动全套服务
docker-compose up -d

# 仅启动数据库
docker-compose up -d mysql redis
```

## 环境配置

### 数据库连接
默认连接字符串：`mysql+pymysql://root:password@localhost:3306/logwatcher`

通过环境变量 `DATABASE_URL` 覆盖。

### 服务端口
- 后端: 8000 (开发) / 28000 (Docker)
- 前端: 5173 (开发) / 23000 (Docker)  
- MySQL: 3306 (本地) / 23307 (Docker)
- Redis: 6379 (本地) / 26379 (Docker)

### CORS 配置
后端已配置允许来自 `http://localhost:3000` 和 `http://localhost:5173` 的跨域请求。

## 关键代码位置

### 收集器系统
- `backend/collectors/base.py` - 基础收集器抽象类
- `backend/collectors/manager.py` - 收集器管理器
- `backend/collectors/ai_news_collector.py` - AI新闻收集器
- `backend/collectors/cursor_collector.py` - Cursor更新收集器

### WebSocket 管理
- `backend/websocket_manager.py` - WebSocket连接管理
- `backend/main.py:49` - WebSocket路由端点

### 数据库层
- `backend/database.py` - 数据库连接和会话管理
- `backend/models.py` - 数据模型定义

## 添加新收集器

1. 在 `backend/collectors/` 创建新的收集器文件
2. 继承 `BaseCollector` 类并实现 `collect()` 方法
3. 在 `backend/collectors/manager.py` 中注册新收集器
4. 在相应的路由中添加 API 端点

## 数据流向

1. 收集器定期抓取数据源
2. 数据通过 CollectorManager 处理和存储
3. API 路由提供数据查询接口
4. WebSocket 推送实时更新
5. 前端通过 API 获取数据并渲染

