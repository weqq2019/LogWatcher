# AI新闻收集配置

## 配置说明

现在AI新闻收集的次数限制和模型都已经改为可配置的变量，你可以通过以下方式修改：

## 🔢 每日收集次数限制配置

### 方法1：环境变量配置（推荐）

在你的环境变量中设置：
```bash
export DAILY_AI_COLLECT_LIMIT=5
```

或者在 `.env` 文件中添加：
```
DAILY_AI_COLLECT_LIMIT=5
```

### 方法2：直接修改配置文件

在 `backend/config.py` 文件中找到：
```python
self.daily_ai_collect_limit = int(os.getenv("DAILY_AI_COLLECT_LIMIT", "5"))
```

修改默认值 `"5"` 为你想要的次数，例如 `"10"`：
```python
self.daily_ai_collect_limit = int(os.getenv("DAILY_AI_COLLECT_LIMIT", "10"))
```

## 🤖 AI模型配置

### 方法1：环境变量配置（推荐）

在你的环境变量中设置：
```bash
export AI_MODEL=deepseek-v3
```

或者在 `.env` 文件中添加：
```
AI_MODEL=deepseek-v3
```

### 方法2：直接修改配置文件

在 `backend/config.py` 文件中找到：
```python
self.ai_model = os.getenv("AI_MODEL", "deepseek-r1")
```

修改默认值 `"deepseek-r1"` 为你想要的模型，例如 `"deepseek-v3"`：
```python
self.ai_model = os.getenv("AI_MODEL", "deepseek-v3")
```

### 支持的模型列表
- `deepseek-r1` (默认)
- `deepseek-v3`
- `grok-3`
- `grok-2`
- 其他兼容的模型

## 重启应用

修改后需要重启后端应用才能生效：
```bash
# 如果使用Docker
docker-compose restart backend

# 如果直接运行
# 重启你的FastAPI应用
```

## 配置示例

完整的 `.env` 文件示例：
```
# AI新闻收集配置
DAILY_AI_COLLECT_LIMIT=5
AI_MODEL=deepseek-v3

# 其他配置...
DATABASE_URL=mysql+pymysql://logwatcher:logwatcher123@mysql:3306/logwatcher
DEEPSEEK_API_KEY=your_api_key_here
```

## 数据库迁移

如果你是现有用户，需要执行数据库迁移来添加模型字段：

```bash
# 连接到你的MySQL数据库
mysql -u root -p logwatcher

# 或者使用docker
docker exec -it logwatcher-mysql mysql -u logwatcher -p logwatcher

# 执行迁移脚本
source database_migration_add_model.sql
```

## 说明

- **次数限制**：默认每日5次，修改后前端界面会自动显示新的限制次数
- **AI模型**：默认使用 `grok-3-deepsearch`，修改后前端界面会自动显示当前使用的模型
- **模型显示**：前端新闻列表会显示每条新闻的来源模型（🤖 模型名称）
- 所有相关的提示信息都会自动更新
- 配置立即生效，无需修改前端代码 