# 工具API使用指南

## 概述

本系统支持三种类型的工具：
1. **内置工具** - 系统预置的工具（如时间查询、计算器等）
2. **外部API工具** - 调用外部HTTP API的工具
3. **自定义代码工具** - 使用Python代码实现的工具

## 工具API定义位置

### 1. 内置工具定义

内置工具在后端 `app.py` 中定义，使用装饰器注册：

```python
@register_builtin_tool('工具名称')
def tool_function(params):
    """工具功能描述"""
    # 实现逻辑
    return {
        'success': True,
        'result': {...}
    }
```

#### 内置工具示例

**获取当前时间**
```python
@register_builtin_tool('get_current_time')
def tool_get_current_time(params):
    """获取当前时间"""
    from datetime import datetime
    timezone = params.get('timezone', 'UTC')
    now = datetime.now()
    return {
        'success': True,
        'result': {
            'time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'timezone': timezone,
            'timestamp': int(now.timestamp())
        }
    }
```

**计算器**
```python
@register_builtin_tool('calculate')
def tool_calculate(params):
    """计算数学表达式"""
    try:
        expression = params.get('expression', '')
        result = eval(expression, {"__builtins__": {}}, {})
        return {
            'success': True,
            'result': {
                'expression': expression,
                'value': result
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### 2. 外部API工具定义

外部API工具通过前端注册，配置以下信息：

- **工具名称**: API工具的标识
- **工具描述**: 告诉模型工具的用途
- **API URL**: 外部API的完整URL
- **HTTP方法**: GET或POST
- **请求头**: JSON格式的HTTP headers
- **参数定义**: JSON Schema格式

#### 外部API示例配置

**天气查询API**
```json
{
  "name": "get_weather",
  "description": "查询指定城市的天气信息",
  "api_url": "https://api.weather.com/v1/current",
  "api_method": "GET",
  "api_headers": {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
  },
  "parameters": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "城市名称"
      }
    },
    "required": ["city"]
  }
}
```

### 3. 自定义代码工具定义

自定义代码工具通过前端注册，直接编写Python代码：

- **工具名称**: 代码工具的标识
- **工具描述**: 告诉模型工具的用途
- **Python代码**: 实际执行的代码
- **参数定义**: JSON Schema格式

#### 自定义代码示例

**文本大写转换**
```python
# params 变量包含传入的参数
# 将结果赋值给 result 变量

text = params.get('text', '')
result = {
    'uppercase': text.upper(),
    'length': len(text)
}
```

**参数定义**
```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "要转换的文本"
    }
  },
  "required": ["text"]
}
```

## 工具执行流程

### 1. 工具注册

前端通过 `POST /api/tools/register` 注册工具：

```javascript
fetch('/api/tools/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        name: 'tool_name',
        description: '工具描述',
        parameters: {...},  // JSON Schema
        tool_type: 'builtin|api|code',  // 工具类型
        // 如果是API工具
        api_url: 'https://...',
        api_method: 'POST',
        api_headers: {...},
        // 如果是代码工具
        code: 'Python代码'
    })
})
```

### 2. 工具调用

当对话时启用工具后，流程如下：

1. **用户发送消息** → 包含启用的工具列表
2. **模型收到工具定义** → 决定是否调用工具
3. **模型返回tool_call** → 包含工具名称和参数
4. **后端执行工具** → 调用 `execute_tool_call()`
5. **返回工具结果** → 添加到对话历史
6. **模型继续回答** → 基于工具结果生成最终答案

### 3. 工具执行API

手动执行工具：`POST /api/tools/execute`

```javascript
fetch('/api/tools/execute', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        tool_name: 'calculate',
        parameters: {
            expression: '2 + 3 * 4'
        }
    })
})
```

响应：
```json
{
    "success": true,
    "result": {
        "expression": "2 + 3 * 4",
        "value": 14
    }
}
```

## JSON Schema 格式说明

工具参数使用JSON Schema定义，常用字段：

```json
{
  "type": "object",
  "properties": {
    "param1": {
      "type": "string",
      "description": "参数1的描述"
    },
    "param2": {
      "type": "number",
      "description": "参数2的描述"
    },
    "param3": {
      "type": "boolean",
      "description": "参数3的描述"
    }
  },
  "required": ["param1"]  // 必填参数列表
}
```

### 数据类型

- `string` - 字符串
- `number` - 数字
- `integer` - 整数
- `boolean` - 布尔值
- `array` - 数组
- `object` - 对象

### 高级示例

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "搜索关键词"
    },
    "filters": {
      "type": "object",
      "properties": {
        "category": {
          "type": "string",
          "enum": ["news", "blogs", "videos"]
        },
        "limit": {
          "type": "integer",
          "minimum": 1,
          "maximum": 100
        }
      }
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": ["query"]
}
```

## 使用示例

### 在对话中使用工具

1. **注册工具** - 在"工具管理"页面注册工具
2. **选择模型** - 在"智能对话"页面选择支持工具调用的模型
3. **激活工具** - 勾选要使用的工具
4. **发起对话** - 发送消息，模型会自动调用工具

示例对话：
```
用户: 帮我计算 123 * 456
模型: [调用 calculate 工具]
    参数: {"expression": "123 * 456"}
    结果: {"value": 56088}
模型: 计算结果是 56088
```

### 扩展内置工具

在 `app.py` 中添加新的内置工具：

```python
@register_builtin_tool('your_tool_name')
def tool_your_function(params):
    """工具描述"""
    # 从params获取参数
    param1 = params.get('param1')
    param2 = params.get('param2', 'default')
    
    try:
        # 执行逻辑
        result_data = do_something(param1, param2)
        
        # 返回成功结果
        return {
            'success': True,
            'result': result_data
        }
    except Exception as e:
        # 返回错误
        return {
            'success': False,
            'error': str(e)
        }
```

然后在 `get_builtin_tools()` 函数的 `builtin_schemas` 中添加Schema定义。

## 安全注意事项

1. **代码工具**: 自定义代码在服务器端执行，需要严格的安全审查
2. **API工具**: 外部API可能泄露敏感信息，建议使用白名单
3. **参数验证**: 所有工具都应验证输入参数
4. **错误处理**: 工具执行失败时应返回明确的错误信息
5. **超时设置**: API调用应设置合理的超时时间

## 故障排查

### 工具未被调用
- 检查工具是否已在对话中激活
- 确认模型支持工具调用（Function Calling）
- 检查工具描述是否清晰，让模型理解

### 工具执行失败
- 查看后端日志获取详细错误信息
- 验证参数格式是否正确
- 测试外部API是否可访问
- 检查自定义代码语法

### 工具返回格式错误
- 确保返回格式为 `{'success': bool, 'result': any}` 或 `{'success': False, 'error': str}`
- 检查JSON编码问题
- 验证数据类型匹配

## API参考

### GET /api/tools
获取所有已注册的工具

### POST /api/tools/register
注册新工具

### DELETE /api/tools/<tool_id>
删除工具

### POST /api/tools/<tool_id>/toggle
启用/禁用工具

### GET /api/tools/builtin
获取内置工具列表

### POST /api/tools/execute
手动执行工具调用

