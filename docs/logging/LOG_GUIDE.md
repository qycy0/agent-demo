# 📋 日志系统使用指南

## 📖 概述

系统已集成完整的日志功能，用于调试和监控所有请求、模型调用和工具执行。

---

## 📁 日志文件

### 主日志文件
- **位置**: `/mnt/zhizhu/mobile-agent/app.log`
- **格式**: `时间戳 [级别] 模块名 - 消息`
- **编码**: UTF-8
- **输出**: 同时输出到文件和控制台

---

## 🔍 日志级别

| 级别 | 用途 | 示例 |
|------|------|------|
| **DEBUG** | 详细信息 | 请求参数、响应内容 |
| **INFO** | 一般信息 | 请求开始、工具执行 |
| **WARNING** | 警告信息 | 参数缺失、降级操作 |
| **ERROR** | 错误信息 | 异常、调用失败 |

当前配置: **DEBUG** (所有日志都会记录)

---

## 📊 日志内容

### 1. HTTP 请求日志

每个 HTTP 请求都会记录：

```
2024-12-04 12:00:00 [INFO] __main__ - ━━━━ 新请求 ━━━━
2024-12-04 12:00:00 [INFO] __main__ - Method: POST
2024-12-04 12:00:00 [INFO] __main__ - Path: /api/chat/mcp
2024-12-04 12:00:00 [INFO] __main__ - IP: 127.0.0.1
2024-12-04 12:00:00 [INFO] __main__ - Request Data: messages=[3 items], ...
2024-12-04 12:00:01 [INFO] __main__ - Response Status: 200
2024-12-04 12:00:01 [INFO] __main__ - ━━━━ 请求结束 ━━━━
```

### 2. 模型调用日志

```
2024-12-04 12:00:00 [INFO] __main__ - 🤖 调用模型: GPT-4
2024-12-04 12:00:00 [DEBUG] __main__ -    模型类型: openai
2024-12-04 12:00:00 [DEBUG] __main__ -    URL: https://api.openai.com/v1
2024-12-04 12:00:00 [DEBUG] __main__ -    消息数量: 3
2024-12-04 12:00:00 [DEBUG] __main__ -    工具数量: 2
2024-12-04 12:00:00 [DEBUG] __main__ -    参数: {'temperature': 0.7, ...}
2024-12-04 12:00:00 [DEBUG] __main__ -    请求数据: {
  "messages": [
    {"role": "system", "content": "You are a helpful assistant..."},
    {"role": "user", "content": "现在几点？"}
  ],
  "temperature": 0.7,
  "model": "gpt-4-turbo"
}
2024-12-04 12:00:00 [DEBUG] __main__ -    发送请求到: https://api.openai.com/v1/chat/completions
2024-12-04 12:00:00 [DEBUG] __main__ -    响应状态: 200
2024-12-04 12:00:02 [INFO] __main__ -    ✅ 模型响应完成 (长度: 156 字符)
2024-12-04 12:00:02 [DEBUG] __main__ -    响应内容: <think>用户询问时间，我需要调用get_current_time工具</think><tool_call>{"name":"get_current_time"...
```

### 3. MCP 协调日志

```
2024-12-04 12:00:00 [INFO] mcp - 🔄 MCP协调开始
2024-12-04 12:00:00 [DEBUG] mcp -    消息数量: 3
2024-12-04 12:00:00 [DEBUG] mcp -    工具数量: 2
2024-12-04 12:00:00 [DEBUG] mcp -    自动解析: True
2024-12-04 12:00:00 [DEBUG] mcp -    最大迭代: 5
2024-12-04 12:00:00 [INFO] mcp -    🔁 第 1 轮迭代开始
```

### 4. 工具执行日志

```
2024-12-04 12:00:01 [INFO] mcp -       🔧 执行工具: get_current_time
2024-12-04 12:00:01 [DEBUG] mcp -          参数: {"timezone":"Asia/Shanghai"}
2024-12-04 12:00:01 [INFO] __main__ - 🔧 执行工具调用: get_current_time
2024-12-04 12:00:01 [DEBUG] __main__ -    参数: {"timezone":"Asia/Shanghai"}
2024-12-04 12:00:01 [INFO] __main__ -    使用内置工具: get_current_time
2024-12-04 12:00:01 [INFO] __main__ -    ✅ 执行成功 (0.02s)
2024-12-04 12:00:01 [DEBUG] __main__ -    结果: {"success":true,"result":{...}}
2024-12-04 12:00:01 [INFO] mcp -          ✅ 工具执行成功
```

---

## 🛠️ 查看日志

### 方法 1: 实时查看（推荐）

```bash
# 查看所有日志
tail -f app.log

# 只看 INFO 及以上级别
tail -f app.log | grep -E 'INFO|WARNING|ERROR'

# 只看错误
tail -f app.log | grep ERROR

# 只看工具调用
tail -f app.log | grep "🔧"

# 只看模型调用
tail -f app.log | grep "🤖"
```

### 方法 2: 搜索日志

```bash
# 搜索特定工具
grep "get_current_time" app.log

# 搜索错误
grep ERROR app.log

# 搜索特定时间段（12:00-13:00）
grep "12:[0-5][0-9]:" app.log

# 搜索特定IP的请求
grep "IP: 192.168.1.100" app.log
```

### 方法 3: 分析日志

```bash
# 统计工具调用次数
grep "🔧 执行工具:" app.log | wc -l

# 统计各工具调用次数
grep "🔧 执行工具:" app.log | awk '{print $NF}' | sort | uniq -c

# 查看最近的错误
grep ERROR app.log | tail -20

# 按请求分组查看
grep "━━━━" app.log
```

---

## 📈 日志管理

### 日志轮转

建议配置日志轮转以防止日志文件过大：

```bash
# 安装 logrotate（如果没有）
sudo apt-get install logrotate

# 创建配置文件
sudo vim /etc/logrotate.d/mobile-agent
```

配置内容：
```
/mnt/zhizhu/mobile-agent/app.log {
    daily                  # 每天轮转
    rotate 7               # 保留7天
    compress               # 压缩旧日志
    delaycompress          # 延迟压缩
    missingok              # 文件不存在不报错
    notifempty             # 空文件不轮转
    create 0644 root root  # 创建新文件的权限
}
```

### 手动清理

```bash
# 清空日志文件（保留文件）
> app.log

# 删除旧日志
rm app.log

# 查看日志文件大小
ls -lh app.log

# 只保留最近1000行
tail -1000 app.log > app.log.tmp && mv app.log.tmp app.log
```

---

## 🔧 调整日志级别

### 临时调整（重启后恢复）

在 `app.py` 中修改：

```python
# 只记录 INFO 及以上
logging.basicConfig(level=logging.INFO, ...)

# 只记录 WARNING 及以上
logging.basicConfig(level=logging.WARNING, ...)

# 记录所有（包括 DEBUG）
logging.basicConfig(level=logging.DEBUG, ...)
```

### 动态调整（运行时）

```python
# 在 Python 控制台或代码中
import logging
logging.getLogger().setLevel(logging.INFO)
```

---

## 📝 自定义日志

### 在新代码中添加日志

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("详细调试信息")
    logger.info("一般信息")
    logger.warning("警告信息")
    logger.error("错误信息")
    
    try:
        # 业务逻辑
        logger.info(f"🔧 执行操作: {operation}")
        result = do_something()
        logger.info(f"   ✅ 操作成功")
        logger.debug(f"   结果: {result}")
    except Exception as e:
        logger.error(f"   ❌ 操作失败: {e}")
        logger.error(traceback.format_exc())
```

### 日志格式化

当前格式：
```
%(asctime)s [%(levelname)s] %(name)s - %(message)s
```

可自定义为：
```python
format='%(asctime)s [%(levelname)8s] [%(name)20s] %(funcName)s:%(lineno)d - %(message)s'
```

---

## 🎯 常见调试场景

### 场景 1: 调试工具调用

```bash
# 查看所有工具调用
grep "🔧 执行工具" app.log

# 查看工具调用的参数和结果
grep -A 10 "🔧 执行工具: get_current_time" app.log

# 查看工具失败
grep "❌.*工具" app.log
```

### 场景 2: 调试模型请求

```bash
# 查看模型调用
grep "🤖 调用模型" app.log

# 查看模型调用的详细信息
grep -A 5 "🤖 调用模型" app.log

# 查看某个模型的所有调用
grep "调用模型: GPT-4" app.log
```

### 场景 3: 调试 MCP 协调

```bash
# 查看 MCP 开始
grep "🔄 MCP协调开始" app.log

# 查看迭代过程
grep "🔁 第.*轮迭代" app.log

# 查看完整的 MCP 会话
grep -E "🔄|🔁|🔧" app.log
```

### 场景 4: 查看错误

```bash
# 所有错误
grep ERROR app.log

# 错误的上下文（前后5行）
grep -C 5 ERROR app.log

# 最近的错误
grep ERROR app.log | tail -20

# 错误统计
grep ERROR app.log | wc -l
```

### 场景 5: 性能分析

```bash
# 查看工具执行时间
grep "执行成功" app.log | grep -o "([0-9.]*s)"

# 查看慢请求（超过1秒）
grep "([1-9][0-9]*\.[0-9]*s)" app.log

# 统计平均响应时间
# (需要自定义脚本)
```

---

## 📦 日志备份

### 定期备份

```bash
# 按日期备份
cp app.log app-$(date +%Y%m%d).log

# 压缩备份
tar -czf logs-$(date +%Y%m%d).tar.gz app.log

# 备份到其他位置
cp app.log /backup/mobile-agent/app-$(date +%Y%m%d).log
```

### 自动备份脚本

```bash
#!/bin/bash
# backup_logs.sh

BACKUP_DIR="/backup/mobile-agent"
mkdir -p $BACKUP_DIR

DATE=$(date +%Y%m%d)
cp /mnt/zhizhu/mobile-agent/app.log $BACKUP_DIR/app-$DATE.log
gzip $BACKUP_DIR/app-$DATE.log

# 删除30天前的备份
find $BACKUP_DIR -name "app-*.log.gz" -mtime +30 -delete
```

添加到 crontab：
```bash
# 每天凌晨2点备份
0 2 * * * /path/to/backup_logs.sh
```

---

## 🚨 监控和告警

### 简单监控

```bash
# 检查是否有错误
if grep -q ERROR app.log; then
    echo "发现错误！" | mail -s "Mobile-Agent Error" admin@example.com
fi

# 检查工具失败率
TOTAL=$(grep "🔧 执行工具" app.log | wc -l)
FAILED=$(grep "❌.*工具执行" app.log | wc -l)
if [ $TOTAL -gt 0 ]; then
    RATE=$(echo "scale=2; $FAILED/$TOTAL*100" | bc)
    if [ $(echo "$RATE > 10" | bc) -eq 1 ]; then
        echo "工具失败率过高: $RATE%" | mail -s "Alert" admin@example.com
    fi
fi
```

---

## 💡 最佳实践

1. **定期查看日志**: 每天检查是否有异常
2. **配置日志轮转**: 防止日志文件过大
3. **重要操作前查看**: 确保系统运行正常
4. **出错时查看上下文**: 使用 `grep -C` 查看前后文
5. **保留足够的历史**: 至少保留7天的日志
6. **监控关键指标**: 错误率、响应时间等
7. **使用日志分析工具**: 如 ELK、Grafana 等

---

## 🔗 相关文档

- **系统文档**: `README.md`
- **MCP 指南**: `MCP_GUIDE.md`
- **工具开发**: `BUILTIN_TOOLS_GUIDE.md`

---

**版本**: v1.0  
**更新日期**: 2024-12-04  
**维护者**: Development Team

