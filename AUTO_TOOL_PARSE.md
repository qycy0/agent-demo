# 自动工具调用解析 - 使用指南

## 🎯 功能概述

**自动工具调用解析**功能允许模型在其输出中直接编写工具调用代码，系统会自动识别、解析并执行这些工具调用，然后在对话中展示执行结果。

## 🚀 快速开始

### 第1步: 启用功能

1. 打开网页 → **智能对话**页面
2. 在左侧配置区域找到 **🔧 启用工具** 部分
3. 勾选 **🤖 自动解析工具调用** 开关（会变成红色）
4. 勾选要使用的工具（如 `calculate`, `get_current_time`）

### 第2步: 配置模型系统提示词

为了让模型知道如何编写工具调用，建议在模型配置中添加系统提示词：

```
你是一个智能助手，可以使用工具来帮助用户。

当需要使用工具时，请在输出中使用以下格式：
<tool_call>
{"name": "工具名", "arguments": {参数字典}}
</tool_call>

可用工具：
- calculate: 计算数学表达式，参数 expression
- get_current_time: 获取当前时间，参数 timezone
- search_web: 搜索信息，参数 query

示例：
<tool_call>
{"name": "calculate", "arguments": {"expression": "2 + 3 * 4"}}
</tool_call>
```

### 第3步: 开始对话

直接发送需要使用工具的问题，模型会自动调用工具！

## 📝 工具调用格式

系统支持三种工具调用格式：

### 格式1: 标准JSON格式（推荐）

```xml
<tool_call>
{"name": "calculate", "arguments": {"expression": "123 * 456"}}
</tool_call>
```

### 格式2: XML属性格式

```xml
<tool_call name="calculate" arguments='{"expression": "123 * 456"}'/>
```

### 格式3: 函数调用格式（在</think>后）

```javascript
calculate({"expression": "123 * 456"})
```

**注意**: 格式3只会解析`</think>`标签之后的函数调用。

## 💡 使用示例

### 示例1: 简单计算

**用户输入**:
```
帮我算一下 123 乘以 456 等于多少？
```

**模型输出**:
```
<think>
用户需要计算123乘以456，我应该使用calculate工具
</think>

好的，让我帮你计算：

<tool_call>
{"name": "calculate", "arguments": {"expression": "123 * 456"}}
</tool_call>
```

**系统自动执行后显示**:
```
好的，让我帮你计算：

🔧 执行工具调用
━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 calculate
参数: {"expression": "123 * 456"}
✅ 结果: {
  "expression": "123 * 456",
  "value": 56088
}
```

### 示例2: 多个工具调用

**用户输入**:
```
现在几点了？顺便帮我算一下2的10次方
```

**模型输出**:
```
<think>
需要使用两个工具：
1. get_current_time 查询时间
2. calculate 计算2^10
</think>

让我帮你查询：

<tool_call>
{"name": "get_current_time", "arguments": {"timezone": "Asia/Shanghai"}}
</tool_call>

<tool_call>
{"name": "calculate", "arguments": {"expression": "2 ** 10"}}
</tool_call>
```

**系统自动执行后显示**:
```
让我帮你查询：

🔧 执行工具调用
━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 get_current_time
参数: {"timezone": "Asia/Shanghai"}
✅ 结果: {
  "time": "2024-12-03 14:30:00",
  "timezone": "Asia/Shanghai",
  "timestamp": 1701594600
}
━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 calculate
参数: {"expression": "2 ** 10"}
✅ 结果: {
  "expression": "2 ** 10",
  "value": 1024
}
```

### 示例3: 工具调用失败

**模型输出**:
```
<tool_call>
{"name": "non_existent_tool", "arguments": {}}
</tool_call>
```

**系统显示**:
```
🔧 执行工具调用
━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 non_existent_tool
参数: {}
❌ 错误: 工具 non_existent_tool 未注册
```

## 🎨 结果展示说明

### 成功状态（绿色背景）
```
✅ 结果: {...}
```
- 工具成功执行
- 显示完整的返回结果
- JSON格式化显示

### 失败状态（红色背景）
```
❌ 错误: 错误信息
```
- 工具执行失败
- 显示具体错误原因
- 帮助调试问题

### 执行中状态
```
⏳ 执行中...
```
- 工具正在执行
- 稍后更新为最终结果

## 🔧 高级配置

### 自定义工具调用格式

如果你的模型使用不同的格式，可以修改 `app.js` 中的 `autoParseAndExecuteTools` 函数：

```javascript
// 添加自定义正则表达式
const customRegex = /你的正则表达式/g;
while ((match = customRegex.exec(content)) !== null) {
    // 解析逻辑
}
```

### 结果样式自定义

修改 `style.css` 中的相关类：

```css
.tool-execution-results {
    /* 自定义容器样式 */
}

.tool-result.success {
    /* 自定义成功状态样式 */
}

.tool-result.error {
    /* 自定义错误状态样式 */
}
```

## 📋 注意事项

### ✅ 最佳实践

1. **明确的系统提示**: 在系统提示词中清楚说明工具调用格式
2. **工具描述完整**: 确保每个工具都有清晰的描述和参数说明
3. **参数验证**: 工具应该验证输入参数的有效性
4. **错误处理**: 工具执行应该有完善的错误处理

### ⚠️ 常见问题

**Q: 工具没有被执行？**
- 确认"自动解析工具调用"开关已启用（红色状态）
- 检查工具调用格式是否正确
- 查看浏览器控制台的错误信息

**Q: JSON解析失败？**
- 确保JSON格式正确（双引号，正确的括号配对）
- 检查特殊字符是否需要转义
- 使用JSON验证工具检查格式

**Q: 工具执行失败？**
- 确认工具已在"工具管理"中注册
- 检查参数名称和类型是否匹配
- 查看后端终端的错误日志

**Q: 多个工具调用顺序？**
- 系统按出现顺序并发执行
- 如需保证顺序，可以让模型分多轮对话

### 🔒 安全限制

- **仅执行已注册工具**: 未注册的工具调用会被拒绝
- **参数类型检查**: 参数会根据JSON Schema验证
- **结果大小限制**: 超长结果会被截断显示
- **执行超时**: 工具执行超时会返回错误

## 🔄 与手动选择工具的区别

### 手动选择（传统方式）
- 用户勾选工具
- 模型决定是否调用
- 模型发起tool_call请求
- 系统执行并返回
- 需要模型支持Function Calling

### 自动解析（新方式）
- 用户勾选工具和自动解析
- 模型在输出中编写工具调用
- 系统自动识别和解析
- 立即执行并显示结果
- 任何模型都可以使用（只要会写格式）

## 🎓 教学建议

### 教模型使用工具

在系统提示词中提供完整示例：

```
你可以使用以下工具：

1. calculate - 计算数学表达式
   格式: <tool_call>{"name": "calculate", "arguments": {"expression": "表达式"}}</tool_call>
   示例: <tool_call>{"name": "calculate", "arguments": {"expression": "2 + 3"}}</tool_call>

2. get_current_time - 获取当前时间
   格式: <tool_call>{"name": "get_current_time", "arguments": {"timezone": "时区"}}</tool_call>
   示例: <tool_call>{"name": "get_current_time", "arguments": {"timezone": "UTC"}}</tool_call>

使用规则：
- 在<think></think>中思考是否需要工具
- 在正文中编写工具调用
- 一次可以调用多个工具
- 等待系统执行后再给出最终答案
```

## 📚 相关文档

- **工具API文档**: `TOOL_API.md`
- **工具快速入门**: `QUICKSTART_TOOLS.md`
- **更新日志**: `CHANGELOG.md` (v2.6)
- **测试脚本**: `test_tools.py`

## 🤝 反馈与支持

遇到问题？
1. 查看浏览器控制台（F12）的错误信息
2. 查看服务器终端的日志输出
3. 检查 `CHANGELOG.md` 的已知问题
4. 运行 `python test_tools.py` 验证工具功能

---

**开始使用自动工具调用，让AI更智能！** 🚀

