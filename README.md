# 行业智能通用运维模型2.0

**版本**: v2.7.5 | **更新日期**: 2024-12-04

一个功能完整的行业级智能运维平台，支持模型注册、工具管理、智能对话和多轮工具调用。

## 📚 文档导航

- **[📖 完整文档索引](docs/INDEX.md)** - 所有文档的导航中心
- **[📝 使用指南](docs/USAGE.md)** - 基础操作指南
- **[🔧 工具开发](docs/guides/BUILTIN_TOOLS_GUIDE.md)** - 开发内置工具
- **[🔄 MCP 系统](docs/guides/MCP_GUIDE.md)** - Model Context Protocol 详解
- **[📊 日志系统](docs/logging/LOG_GUIDE.md)** - 日志使用和调试
- **[📋 更新日志](CHANGELOG.md)** - 完整版本历史
- **[✨ 功能概览](FEATURES.md)** - 所有功能列表

## 功能特性

### 🎯 模型管理
- 支持多种模型类型（OpenAI、Claude、自定义）
- 模型连接测试和验证
- 动态模型注册、编辑和删除
- 支持 API Key 认证
- 自定义系统提示词

### 🔧 工具管理
- **三种工具类型**：内置工具、外部 API、自定义代码
- JSON Schema 参数定义
- 工具启用/禁用控制
- 工具动态加载
- 模块化内置工具开发

### 💬 智能对话
- **流式输出**：实时显示模型思考过程
- **多模态输入**：支持文本、图片、视频上传
- **模型参数**：Temperature、Max Tokens、Top P、Presence/Frequency Penalty
- **工具调用**：自动解析和执行工具
- **对话历史**：完整的多轮对话管理
- **详情面板**：查看模型 thinking 和工具执行过程

### 🔄 MCP 系统 (Model Context Protocol)
- **自动多轮调用**：模型自动调用工具直到获得最终答案
- **工具编排**：智能管理工具调用顺序和结果
- **过程可视化**：实时显示 thinking、工具调用状态
- **错误处理**：优雅处理工具执行失败
- **详细日志**：完整记录每轮交互过程

### 📊 日志系统
- **完整请求日志**：记录所有 HTTP 请求和响应
- **模型调用日志**：完整的请求参数和返回内容
- **工具执行日志**：参数、结果、执行时间
- **MCP 协调日志**：多轮交互的完整过程
- **日志级别控制**：DEBUG/INFO/WARNING/ERROR
- **实时监控**：`tail -f app.log` 实时查看

## 快速开始

### 1. 安装依赖

```bash
cd /mnt/zhizhu/mobile-agent
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

或使用启动脚本：

```bash
bash start.sh
```

### 3. 访问界面

打开浏览器访问：`http://localhost:5000`

## 使用指南

### 注册模型

1. 点击左侧导航栏的 **"模型管理"**
2. 点击 **"+ 注册新模型"** 按钮
3. 填写模型信息：
   - **模型名称**：自定义名称（如 GPT-4）
   - **API URL**：模型 API 地址（如 `https://api.openai.com/v1`）
   - **API Key**：认证密钥（可选）
   - **模型类型**：选择 OpenAI 兼容、Claude 或自定义
4. 点击 **"测试连接"** 验证配置
5. 测试通过后点击 **"保存"**

### 注册工具

1. 点击左侧导航栏的 **"工具管理"**
2. 点击 **"+ 注册新工具"** 按钮
3. 填写工具信息：
   - **工具名称**：函数名（如 `web_search`）
   - **工具描述**：功能说明
   - **参数定义**：JSON Schema 格式的参数定义
4. 点击 **"保存"**

#### 工具参数示例

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "搜索关键词"
    },
    "limit": {
      "type": "integer",
      "description": "返回结果数量",
      "default": 10
    }
  },
  "required": ["query"]
}
```

### 开始对话

1. 点击左侧导航栏的 **"对话"**
2. 在配置面板中：
   - 选择要使用的模型
   - 输入具体的模型名称（如 `gpt-4`、`claude-3-opus-20240229`）
   - 调整生成参数（Temperature、Max Tokens、Top P）
   - 勾选要激活的工具
   - （可选）上传图片
3. 在输入框中输入消息
4. 点击 **"发送"** 或按 `Enter` 键

## 配置文件

系统配置存储在 `config/` 目录下：

- `models.json`：已注册的模型配置
- `tools.json`：已注册的工具配置

## API 接口

### 模型管理

- `GET /api/models` - 获取所有模型
- `POST /api/models/register` - 注册新模型
- `DELETE /api/models/<model_id>` - 删除模型

### 工具管理

- `GET /api/tools` - 获取所有工具
- `POST /api/tools/register` - 注册新工具
- `DELETE /api/tools/<tool_id>` - 删除工具
- `POST /api/tools/<tool_id>/toggle` - 启用/禁用工具

### 对话

- `POST /api/chat` - 发送对话请求
- `POST /api/upload` - 上传图片

## 目录结构

```
mobile-agent/
├── app.py                    # Flask 后端服务
├── mcp.py                    # MCP 协调器
├── requirements.txt          # Python 依赖
├── start.sh                  # 启动脚本
├── README.md                 # 项目主文档
├── CHANGELOG.md              # 完整更新日志
├── FEATURES.md               # 功能概览
│
├── docs/                     # 📁 文档目录
│   ├── INDEX.md              # 文档索引
│   ├── USAGE.md              # 使用指南
│   ├── guides/               # 详细指南
│   │   ├── MCP_GUIDE.md
│   │   ├── BUILTIN_TOOLS_GUIDE.md
│   │   ├── TOOL_API.md
│   │   └── ...
│   └── logging/              # 日志文档
│       ├── LOG_GUIDE.md
│       └── LOG_EXAMPLE.md
│
├── builtin_tools/            # 📁 内置工具
│   ├── __init__.py
│   ├── schemas.json
│   ├── datetime_tools.py
│   ├── math_tools.py
│   └── search_tools.py
│
├── models/                   # 模型配置
│   └── *.json
├── tools/                    # 工具配置
│   └── *.json
├── uploads/                  # 上传文件
│
└── static/                   # 📁 前端资源
    ├── index.html
    ├── style.css
    └── app.js
```

## 技术栈

### 后端
- **Flask**：Web 框架
- **Flask-CORS**：跨域支持
- **Requests**：HTTP 客户端

### 前端
- **原生 HTML/CSS/JavaScript**
- **响应式设计**
- **现代化 UI**

## 注意事项

1. **API Key 安全**：请妥善保管 API Key，不要泄露给他人
2. **模型兼容性**：确保模型 API 遵循 OpenAI 或 Claude 的接口规范
3. **网络连接**：需要能够访问模型 API 的网络环境
4. **端口占用**：默认使用 5000 端口，如需修改请编辑 `app.py`

## 常见问题

### Q: 模型连接测试失败？
A: 请检查：
- URL 是否正确
- API Key 是否有效
- 网络是否能访问该地址
- 模型类型选择是否正确

### Q: 工具没有被调用？
A: 请确认：
- 工具已启用
- 在对话配置中勾选了该工具
- 工具参数定义正确
- 模型支持 Function Calling

### Q: 图片上传失败？
A: 请检查：
- 图片格式是否支持
- 文件大小是否过大
- `uploads/` 目录是否有写入权限

## 更新日志

### 最新版本 v2.7.5 (2024-12-04)
- ✨ 完整的日志系统（记录请求/响应/工具执行）
- 📊 模型调用参数和返回结果日志
- 🔍 详细的调试信息
- 📝 文档整理和索引优化

### 主要版本里程碑
- **v2.7.x** - 日志系统、内置工具模块化、状态管理优化
- **v2.6.x** - MCP 系统、多轮工具调用、详情面板
- **v2.5.x** - 流式输出、thinking 显示、工具自动解析
- **v2.0.x** - 完整重构、现代化 UI、模型管理

**[查看完整更新日志 →](CHANGELOG.md)**

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。

