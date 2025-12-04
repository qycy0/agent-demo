# 📚 行业智能通用运维模型 2.0 - 文档索引

**版本**: v2.7.5  
**更新日期**: 2024-12-04

---

## 🚀 快速开始

### 新手入门
1. [README.md](../README.md) - 项目概述和快速开始
2. [USAGE.md](USAGE.md) - 基础使用指南
3. [FEATURES.md](../FEATURES.md) - 功能概览

### 核心功能
- **智能对话**: 支持多模态输入（文本、图片、视频）
- **工具系统**: 可扩展的工具注册和调用
- **MCP 协调**: 自动多轮工具调用
- **流式输出**: 实时显示模型思考过程

---

## 📖 详细指南

### 工具系统

#### [guides/TOOL_API.md](guides/TOOL_API.md)
**工具 API 完整文档**
- 工具定义格式
- 三种工具类型（内置、API、代码）
- JSON Schema 参数定义
- 工具注册和管理

#### [guides/QUICKSTART_TOOLS.md](guides/QUICKSTART_TOOLS.md)
**工具快速入门**
- 5 分钟上手
- 常见示例
- 最佳实践

#### [guides/BUILTIN_TOOLS_GUIDE.md](guides/BUILTIN_TOOLS_GUIDE.md)
**内置工具开发指南**
- 如何创建 Built-in 工具
- 模块化开发规范
- 完整示例

#### [guides/AUTO_TOOL_PARSE.md](guides/AUTO_TOOL_PARSE.md)
**自动工具解析**
- 工具调用格式
- 自动解析机制
- 故障排查

### MCP 系统

#### [guides/MCP_GUIDE.md](guides/MCP_GUIDE.md)
**Model Context Protocol 完整指南**
- MCP 架构详解
- 多轮工具调用流程
- 事件类型说明
- 详情面板使用
- 调试技巧

### 日志系统

#### [logging/LOG_GUIDE.md](logging/LOG_GUIDE.md)
**日志系统使用指南**
- 日志级别和配置
- HTTP 请求日志
- 模型调用日志
- 工具执行日志
- MCP 协调日志
- 实用查询命令

#### [logging/LOG_EXAMPLE.md](logging/LOG_EXAMPLE.md)
**日志示例大全**
- 完整请求-响应流程
- 不同场景示例
- 调试技巧
- 性能分析

### 测试

#### [TEST_FEATURES.md](TEST_FEATURES.md)
**功能测试指南**
- 测试脚本使用
- 功能验证
- 问题排查

---

## 📝 参考文档

### [CHANGELOG.md](../CHANGELOG.md)
**完整更新日志**
- v2.0 - v2.7.5 所有版本
- 功能演进历史
- Bug 修复记录
- 性能优化记录

### [requirements.txt](../requirements.txt)
**Python 依赖包**
- Flask
- requests
- pytz
- 其他依赖

---

## 🗂️ 文档结构

```
mobile-agent/
├── README.md                 # 项目主文档
├── CHANGELOG.md              # 完整更新日志
├── FEATURES.md               # 功能概览
├── requirements.txt          # Python 依赖
│
└── docs/                     # 📁 文档目录
    ├── INDEX.md              # 本文件
    ├── USAGE.md              # 使用指南
    ├── TEST_FEATURES.md      # 测试功能
    │
    ├── guides/               # 📁 详细指南
    │   ├── MCP_GUIDE.md
    │   ├── BUILTIN_TOOLS_GUIDE.md
    │   ├── TOOL_API.md
    │   ├── AUTO_TOOL_PARSE.md
    │   └── QUICKSTART_TOOLS.md
    │
    └── logging/              # 📁 日志文档
        ├── LOG_GUIDE.md
        └── LOG_EXAMPLE.md
```

---

## 🎯 常见任务

### 注册模型
1. 打开模型管理页面
2. 填写模型信息（URL、API Key、显示名称）
3. 测试连通性
4. 保存模型

详见：[USAGE.md](USAGE.md) → 模型注册

### 注册工具
1. 打开工具管理页面
2. 选择工具类型（内置/API/代码）
3. 填写工具定义和参数
4. 激活工具

详见：
- [guides/TOOL_API.md](guides/TOOL_API.md) - 工具定义
- [guides/QUICKSTART_TOOLS.md](guides/QUICKSTART_TOOLS.md) - 快速入门

### 开发内置工具
1. 在 `builtin_tools/` 创建 `xxx_tools.py`
2. 定义工具函数
3. 在 `schemas.json` 添加工具定义
4. 重启应用自动加载

详见：[guides/BUILTIN_TOOLS_GUIDE.md](guides/BUILTIN_TOOLS_GUIDE.md)

### 调试问题
1. 查看日志：`tail -f app.log`
2. 搜索错误：`grep ERROR app.log`
3. 查看请求数据：`grep "请求数据:" app.log -A 20`
4. 查看响应：`grep "响应内容:" app.log`

详见：
- [logging/LOG_GUIDE.md](logging/LOG_GUIDE.md) - 日志使用
- [logging/LOG_EXAMPLE.md](logging/LOG_EXAMPLE.md) - 调试示例

### 理解 MCP 流程
1. 用户发送消息
2. MCP 调用模型
3. 模型返回（可能包含工具调用）
4. MCP 执行工具
5. MCP 将结果返回给模型
6. 重复 2-5 直到模型给出最终答案

详见：[guides/MCP_GUIDE.md](guides/MCP_GUIDE.md)

---

## 💡 学习路径

### 初学者
1. 阅读 [README.md](../README.md)
2. 按照 [USAGE.md](USAGE.md) 完成基础操作
3. 尝试 [guides/QUICKSTART_TOOLS.md](guides/QUICKSTART_TOOLS.md) 的示例
4. 查看 [FEATURES.md](../FEATURES.md) 了解所有功能

### 进阶用户
1. 深入学习 [guides/MCP_GUIDE.md](guides/MCP_GUIDE.md)
2. 学习 [guides/TOOL_API.md](guides/TOOL_API.md) 定义复杂工具
3. 使用 [logging/LOG_GUIDE.md](logging/LOG_GUIDE.md) 调试问题
4. 参考 [guides/BUILTIN_TOOLS_GUIDE.md](guides/BUILTIN_TOOLS_GUIDE.md) 扩展功能

### 开发者
1. 研究 [guides/BUILTIN_TOOLS_GUIDE.md](guides/BUILTIN_TOOLS_GUIDE.md)
2. 理解 [guides/AUTO_TOOL_PARSE.md](guides/AUTO_TOOL_PARSE.md) 机制
3. 掌握 [logging/LOG_EXAMPLE.md](logging/LOG_EXAMPLE.md) 调试技巧
4. 查阅 [CHANGELOG.md](../CHANGELOG.md) 了解实现细节

---

## 🔍 快速查找

### 我想...

#### 注册一个新模型
→ [USAGE.md](USAGE.md) - "模型注册"部分

#### 添加一个工具
→ [guides/QUICKSTART_TOOLS.md](guides/QUICKSTART_TOOLS.md) - "快速开始"

#### 开发内置工具
→ [guides/BUILTIN_TOOLS_GUIDE.md](guides/BUILTIN_TOOLS_GUIDE.md) - "开发流程"

#### 理解工具调用格式
→ [guides/AUTO_TOOL_PARSE.md](guides/AUTO_TOOL_PARSE.md) - "工具调用格式"

#### 查看日志
→ [logging/LOG_GUIDE.md](logging/LOG_GUIDE.md) - "日志位置"

#### 调试工具执行失败
→ [logging/LOG_EXAMPLE.md](logging/LOG_EXAMPLE.md) - "场景3: 工具调用失败"

#### 理解 MCP 工作原理
→ [guides/MCP_GUIDE.md](guides/MCP_GUIDE.md) - "架构详解"

#### 查看更新历史
→ [CHANGELOG.md](../CHANGELOG.md)

#### 了解所有功能
→ [FEATURES.md](../FEATURES.md)

---

## 📞 帮助与支持

### 遇到问题？

1. **查看日志**
   ```bash
   tail -f app.log
   ```

2. **搜索文档**
   - 使用 Ctrl+F 在文档中搜索关键词
   - 查阅 [logging/LOG_EXAMPLE.md](logging/LOG_EXAMPLE.md) 常见问题

3. **查看更新日志**
   - 检查 [CHANGELOG.md](../CHANGELOG.md) 是否有相关 Bug 修复

4. **测试功能**
   - 参考 [TEST_FEATURES.md](TEST_FEATURES.md) 运行测试

---

## 🔄 文档更新

本文档随项目更新而更新。

**最近更新**:
- 2024-12-04: v2.7.5 - 完善日志系统文档
- 2024-12-04: 初始文档索引创建

---

**返回**: [项目主页](../README.md) | **版本**: v2.7.5

