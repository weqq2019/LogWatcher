-- 数据库迁移脚本：添加模型字段到新闻表
-- 执行时间：2025-01-15
-- 描述：为 news_articles 表添加 model 字段来存储AI模型信息

-- 添加 model 字段
ALTER TABLE news_articles 
ADD COLUMN model VARCHAR(100) COMMENT 'AI模型名称' AFTER tags;

-- 更新现有记录的模型信息（可选）
-- 将现有的AI新闻助手记录标记为默认模型
UPDATE news_articles 
SET model = 'grok-3-deepsearch' 
WHERE source = 'AI新闻助手' AND model IS NULL;

-- 创建索引以优化查询性能
CREATE INDEX idx_news_articles_model ON news_articles(model);

-- 验证更改
SELECT COUNT(*) as total_count, 
       COUNT(model) as model_count,
       model
FROM news_articles 
GROUP BY model;

-- 显示表结构
DESCRIBE news_articles; 