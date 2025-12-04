# 使用教程

## 快速上手

### 第一步：启动服务

```bash
cd /mnt/zhizhu/mobile-agent
bash start.sh
```

启动成功后，访问 `http://localhost:5000`

### 第二步：注册模型

#### 示例 1: 注册 OpenAI 模型

1. 点击左侧 **"模型管理"**
2. 点击 **"+ 注册新模型"**
3. 填写信息：
   - 模型名称: `GPT-4`
   - API URL: `https://api.openai.com/v1`
   - API Key: `sk-xxxxxxxxxxxxxxxx`
   - 模型类型: `OpenAI 兼容`
4. 点击 **"测试连接"**
5. 测试成功后点击 **"保存"**

#### 示例 2: 注册 Claude 模型

1. 填写信息：
   - 模型名称: `Claude 3`
   - API URL: `https://api.anthropic.com/v1`
   - API Key: `sk-ant-xxxxxxxxxxxxxxxx`
   - 模型类型: `Claude`
2. 测试并保存

#### 示例 3: 注册自定义模型

1. 填写信息：
   - 模型名称: `本地模型`
   - API URL: `http://localhost:8000/v1`
   - API Key: （可选）
   - 模型类型: `自定义`
2. 测试并保存

### 第三步：注册工具

#### 示例 1: 网页搜索工具

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "搜索关键词"
    },
    "num_results": {
      "type": "integer",
      "description": "返回结果数量",
      "default": 10
    }
  },
  "required": ["query"]
}
```

#### 示例 2: 计算器工具

```json
{
  "type": "object",
  "properties": {
    "expression": {
      "type": "string",
      "description": "数学表达式，例如: 2+3*4"
    }
  },
  "required": ["expression"]
}
```

#### 示例 3: 天气查询工具

```json
{
  "type": "object",
  "properties": {
    "city": {
      "type": "string",
      "description": "城市名称"
    },
    "unit": {
      "type": "string",
      "description": "温度单位",
      "enum": ["celsius", "fahrenheit"],
      "default": "celsius"
    }
  },
  "required": ["city"]
}
```

### 第四步：开始对话

1. 点击左侧 **"对话"**
2. 选择模型（如 `GPT-4`）
3. 输入模型名称（如 `gpt-4-turbo-preview`）
4. 调整参数：
   - Temperature: 0.7（创造性）
   - Max Tokens: 2000（回复长度）
   - Top P: 1.0（多样性）
5. 勾选要使用的工具
6. 输入消息并发送

## 高级功能

### 图片对话

1. 在对话配置面板中点击 **"上传图片"**
2. 选择图片文件
3. 图片会显示在预览区
4. 输入关于图片的问题
5. 发送消息（图片会随消息一起发送）

**注意**：需要模型支持视觉功能（如 GPT-4V、Claude 3）

### 多轮对话

系统会自动保存对话历史，支持上下文连续对话。

点击 **"清空对话"** 可以开始新的对话。

### 工具调用

当模型需要使用工具时：
1. 模型会返回工具调用请求
2. 系统会显示 "🔧 模型调用了 X 个工具"
3. 可以在响应中看到工具调用的结果

## 配置说明

### 模型参数详解

#### Temperature (温度)
- 范围: 0.0 - 2.0
- 推荐值: 0.7
- 说明:
  - 0.0: 最确定性，适合事实性任务
  - 0.7: 平衡创造性和准确性
  - 1.5+: 高创造性，适合创意写作

#### Max Tokens (最大令牌数)
- 范围: 100 - 8000
- 推荐值: 2000
- 说明: 控制回复的最大长度

#### Top P (核采样)
- 范围: 0.0 - 1.0
- 推荐值: 1.0
- 说明: 控制输出的多样性

### 工具参数规范

工具参数必须符合 JSON Schema 规范：

```json
{
  "type": "object",
  "properties": {
    "参数名": {
      "type": "类型",
      "description": "参数描述",
      "enum": ["可选值1", "可选值2"],  // 可选
      "default": "默认值"  // 可选
    }
  },
  "required": ["必需参数1", "必需参数2"]
}
```

支持的类型：
- `string`: 字符串
- `integer`: 整数
- `number`: 数字
- `boolean`: 布尔值
- `array`: 数组
- `object`: 对象

## 常见场景

### 场景 1: 代码助手

1. 注册模型: GPT-4
2. 不启用工具
3. 设置参数:
   - Temperature: 0.3
   - Max Tokens: 4000
4. 提问: "用 Python 写一个快速排序算法"

### 场景 2: 研究助手

1. 注册模型: Claude 3
2. 启用工具: `web_search`
3. 设置参数:
   - Temperature: 0.5
   - Max Tokens: 3000
4. 提问: "最新的人工智能研究进展有哪些？"

### 场景 3: 图片分析

1. 注册模型: GPT-4V
2. 上传图片
3. 设置参数:
   - Temperature: 0.7
   - Max Tokens: 2000
4. 提问: "这张图片中有什么？"

### 场景 4: 数据分析

1. 注册模型: GPT-4
2. 启用工具: `calculator`, `data_analyzer`
3. 设置参数:
   - Temperature: 0.2
   - Max Tokens: 2000
4. 提问: "分析这组数据的趋势"

## 故障排查

### 问题 1: 模型连接失败

**可能原因**:
- URL 错误
- API Key 无效
- 网络问题
- 模型类型选择错误

**解决方法**:
1. 检查 URL 格式是否正确
2. 验证 API Key 是否有效
3. 测试网络连接
4. 确认模型类型匹配

### 问题 2: 工具未被调用

**可能原因**:
- 工具未启用
- 工具未勾选
- 参数定义错误
- 模型不支持 Function Calling

**解决方法**:
1. 在工具管理中启用工具
2. 在对话配置中勾选工具
3. 检查参数定义格式
4. 确认模型支持工具调用

### 问题 3: 图片上传失败

**可能原因**:
- 文件格式不支持
- 文件过大
- 权限问题

**解决方法**:
1. 使用支持的格式（JPG、PNG、GIF）
2. 压缩图片大小
3. 检查 uploads 目录权限

### 问题 4: 响应缓慢

**可能原因**:
- Max Tokens 设置过大
- 模型 API 响应慢
- 网络延迟

**解决方法**:
1. 降低 Max Tokens
2. 更换模型
3. 检查网络状况

## 最佳实践

### 1. 模型选择

- **简单任务**: 使用 GPT-3.5 或小型模型
- **复杂推理**: 使用 GPT-4 或 Claude 3 Opus
- **代码生成**: 使用 GPT-4 或专门的代码模型
- **长文本**: 使用支持大上下文的模型

### 2. 参数调优

- **事实性任务**: Temperature 0.0-0.3
- **创意任务**: Temperature 0.7-1.0
- **平衡任务**: Temperature 0.5-0.7

### 3. 工具使用

- 只启用必要的工具
- 工具描述要清晰准确
- 参数定义要完整

### 4. 对话技巧

- 提供清晰的上下文
- 分步骤提问
- 及时清空无关历史
- 使用具体的指令

## API 集成

如果需要通过 API 调用平台功能：

### 发送对话请求

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "model_1_1234567890",
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "enabled_tools": ["tool_1_1234567890"],
    "params": {
      "model_name": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 2000,
      "top_p": 1.0
    }
  }'
```

### 注册模型

```bash
curl -X POST http://localhost:5000/api/models/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GPT-4",
    "url": "https://api.openai.com/v1",
    "api_key": "sk-xxxxxxxx",
    "model_type": "openai"
  }'
```

### 注册工具

```bash
curl -X POST http://localhost:5000/api/tools/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web_search",
    "description": "搜索网页内容",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "搜索关键词"
        }
      },
      "required": ["query"]
    }
  }'
```

## 更多资源

- [Flask 文档](https://flask.palletsprojects.com/)
- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)
- [Claude API 文档](https://docs.anthropic.com/claude/reference)
- [JSON Schema 规范](https://json-schema.org/)

## 技术支持

如有问题，请查看：
1. README.md - 基础文档
2. 本文档 - 详细使用说明
3. 提交 Issue - 报告问题

