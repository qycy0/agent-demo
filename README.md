# 行业智能通用运维模型2.0

一个功能完整的行业级智能运维平台，支持模型注册、工具管理和智能对话。

## 功能特性

### 🎯 模型管理
- 支持多种模型类型（OpenAI、Claude、自定义）
- 模型连接测试
- 动态模型注册和删除
- 支持 API Key 认证

### 🔧 工具管理
- 自定义工具注册
- JSON Schema 参数定义
- 工具启用/禁用控制
- 工具动态加载

### 💬 对话功能
- 实时对话交互
- 模型参数调节（Temperature、Max Tokens、Top P）
- 图片上传支持
- 工具选择性激活
- 对话历史管理

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
├── app.py                 # Flask 后端服务
├── requirements.txt       # Python 依赖
├── start.sh              # 启动脚本
├── README.md             # 文档
├── config/               # 配置文件目录
│   ├── models.json       # 模型配置
│   └── tools.json        # 工具配置
├── uploads/              # 上传文件目录
└── static/               # 前端文件
    ├── index.html        # 主页面
    ├── style.css         # 样式文件
    └── app.js            # 前端逻辑
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

### v1.0.0 (2024-12-03)
- ✨ 初始版本发布
- 🎯 模型管理功能
- 🔧 工具管理功能
- 💬 对话功能
- 🖼️ 图片上传支持

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。

