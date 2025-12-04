# 📦 Built-in 工具开发指南

本指南介绍如何在系统中添加和管理内置（Built-in）工具。

---

## 📋 目录

1. [什么是 Built-in 工具](#什么是-built-in-工具)
2. [Built-in vs 自定义工具](#built-in-vs-自定义工具)
3. [快速开始](#快速开始)
4. [详细步骤](#详细步骤)
5. [最佳实践](#最佳实践)
6. [示例：完整的工具开发](#示例完整的工具开发)
7. [工具测试](#工具测试)
8. [常见问题](#常见问题)

---

## 什么是 Built-in 工具

**Built-in 工具**是直接集成在系统代码中的工具，具有以下特点：

- ✅ **高性能**: 直接在 Python 中执行，无需网络请求
- ✅ **安全性**: 经过代码审查，可信赖
- ✅ **稳定性**: 随系统一起部署和版本控制
- ✅ **功能强大**: 可以访问系统资源和库
- ✅ **无需配置**: 开箱即用，用户无需设置

**典型用途**:
- 时间日期处理
- 数学计算
- 文件操作
- 数据格式转换
- 系统信息查询

---

## Built-in vs 自定义工具

| 特性 | Built-in 工具 | 自定义工具 |
|------|---------------|------------|
| 添加方式 | 修改代码 | 页面配置 |
| 部署 | 需要重启服务 | 即时生效 |
| 性能 | 高（本地执行） | 取决于实现 |
| 安全性 | 高（代码审查） | 取决于配置 |
| 灵活性 | 低（需要发版） | 高（随时修改） |
| 适用场景 | 核心功能 | 特定业务 |

**选择建议**:
- **Built-in**: 通用、核心、高频使用的功能
- **自定义**: 特定业务、实验性、外部API调用

---

## 快速开始

### 方法 1: 直接在 app.py 中添加（简单）

**步骤**:

1. 打开 `app.py`
2. 找到 "内置工具实现" 部分（约第 305 行）
3. 添加新工具函数
4. 更新 `get_builtin_tools()` 中的 schema
5. 重启服务

**示例**:
```python
# 1. 在 app.py 中添加工具实现
@register_builtin_tool('string_reverse')
def tool_string_reverse(params):
    """反转字符串"""
    text = params.get('text', '')
    return {
        'success': True,
        'result': text[::-1]
    }

# 2. 在 get_builtin_tools() 中添加 schema
builtin_schemas = {
    # ... 现有工具
    'string_reverse': {
        'name': 'string_reverse',
        'description': '反转字符串',
        'parameters': {
            'type': 'object',
            'properties': {
                'text': {
                    'type': 'string',
                    'description': '要反转的字符串'
                }
            },
            'required': ['text']
        }
    }
}
```

**优点**: 快速、简单  
**缺点**: 所有工具在一个文件中，不利于管理

---

### 方法 2: 模块化结构（推荐）

**目录结构**:
```
mobile-agent/
├── app.py
├── builtin_tools/              # 新建目录
│   ├── __init__.py            # 工具加载器
│   ├── schemas.json           # 工具 Schema 配置
│   ├── datetime_tools.py      # 时间日期工具
│   ├── math_tools.py          # 数学计算工具
│   ├── string_tools.py        # 字符串处理工具
│   └── file_tools.py          # 文件操作工具
└── ...
```

**优点**: 
- ✅ 结构清晰，易于维护
- ✅ 工具分类明确
- ✅ 便于团队协作
- ✅ 支持单元测试

---

## 详细步骤

### 步骤 1: 创建目录结构

```bash
cd /mnt/zhizhu/mobile-agent
mkdir -p builtin_tools
touch builtin_tools/__init__.py
touch builtin_tools/schemas.json
```

### 步骤 2: 创建工具文件

**示例**: `builtin_tools/string_tools.py`

```python
"""
字符串处理工具集
"""

def string_reverse(params):
    """
    反转字符串
    
    Args:
        params (dict): 包含 'text' 字段的字典
    
    Returns:
        dict: 包含 success 和 result 的字典
    """
    text = params.get('text', '')
    return {
        'success': True,
        'result': text[::-1]
    }


def string_to_upper(params):
    """
    转换为大写
    
    Args:
        params (dict): 包含 'text' 字段的字典
    
    Returns:
        dict: 包含 success 和 result 的字典
    """
    text = params.get('text', '')
    return {
        'success': True,
        'result': text.upper()
    }


def string_to_lower(params):
    """
    转换为小写
    """
    text = params.get('text', '')
    return {
        'success': True,
        'result': text.lower()
    }
```

### 步骤 3: 定义 Schema

**文件**: `builtin_tools/schemas.json`

```json
{
    "string_reverse": {
        "name": "string_reverse",
        "description": "反转字符串",
        "category": "string",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要反转的字符串"
                }
            },
            "required": ["text"]
        }
    },
    "string_to_upper": {
        "name": "string_to_upper",
        "description": "将字符串转换为大写",
        "category": "string",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要转换的字符串"
                }
            },
            "required": ["text"]
        }
    },
    "string_to_lower": {
        "name": "string_to_lower",
        "description": "将字符串转换为小写",
        "category": "string",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要转换的字符串"
                }
            },
            "required": ["text"]
        }
    }
}
```

### 步骤 4: 创建加载器

**文件**: `builtin_tools/__init__.py`

```python
"""
Built-in 工具加载器
自动发现和注册所有内置工具
"""

import os
import json
import importlib
from pathlib import Path

# 工具注册表
BUILTIN_TOOLS = {}
BUILTIN_SCHEMAS = {}

def load_tools():
    """
    加载所有内置工具
    """
    current_dir = Path(__file__).parent
    
    # 1. 加载 schemas
    schema_file = current_dir / 'schemas.json'
    if schema_file.exists():
        with open(schema_file, 'r', encoding='utf-8') as f:
            BUILTIN_SCHEMAS.update(json.load(f))
    
    # 2. 自动发现并加载所有工具模块
    for file in current_dir.glob('*_tools.py'):
        module_name = file.stem  # 例如: string_tools
        module = importlib.import_module(f'builtin_tools.{module_name}')
        
        # 获取模块中的所有函数
        for name in dir(module):
            if not name.startswith('_'):  # 忽略私有函数
                func = getattr(module, name)
                if callable(func):
                    BUILTIN_TOOLS[name] = func
                    print(f"✓ 加载工具: {name}")
    
    print(f"✓ 共加载 {len(BUILTIN_TOOLS)} 个内置工具")
    return BUILTIN_TOOLS, BUILTIN_SCHEMAS


def get_tool(name):
    """获取指定工具"""
    return BUILTIN_TOOLS.get(name)


def get_schema(name):
    """获取工具的 Schema"""
    return BUILTIN_SCHEMAS.get(name)


def list_tools():
    """列出所有工具"""
    return list(BUILTIN_TOOLS.keys())


def list_schemas():
    """列出所有 Schema"""
    return list(BUILTIN_SCHEMAS.values())


# 自动加载
load_tools()
```

### 步骤 5: 修改 app.py 使用新结构

在 `app.py` 顶部导入：

```python
# 在 app.py 开头添加
try:
    from builtin_tools import BUILTIN_TOOLS, BUILTIN_SCHEMAS, list_schemas
    print("✓ 使用模块化 Built-in 工具")
except ImportError:
    # 降级到原有的内联定义
    print("✓ 使用内联 Built-in 工具")
    BUILTIN_TOOLS = {}
    BUILTIN_SCHEMAS = {}
    
    # 保留原有的 register_builtin_tool 和工具定义
    # ...
```

修改 `get_builtin_tools()` 函数：

```python
@app.route('/api/tools/builtin', methods=['GET'])
def get_builtin_tools():
    """获取内置工具列表"""
    try:
        # 尝试使用模块化的 schemas
        from builtin_tools import list_schemas
        builtin_tools = list_schemas()
    except ImportError:
        # 降级到原有的 builtin_schemas
        builtin_tools = []
        for name in BUILTIN_TOOLS.keys():
            if name in builtin_schemas:
                builtin_tools.append(builtin_schemas[name])
    
    return jsonify({'success': True, 'tools': builtin_tools})
```

### 步骤 6: 重启服务

```bash
cd /mnt/zhizhu/mobile-agent
# 停止现有服务
pkill -f "python.*app.py"

# 启动服务
python app.py

# 或使用 start.sh
./start.sh
```

---

## 最佳实践

### 1. 命名规范

**工具名称**:
- 使用小写字母 + 下划线
- 动词开头，描述性强
- 例如: `get_current_time`, `calculate_sum`, `convert_json`

**文件名称**:
- 按功能分类: `{category}_tools.py`
- 例如: `datetime_tools.py`, `math_tools.py`

### 2. 函数签名

```python
def tool_name(params: dict) -> dict:
    """
    工具描述（一句话）
    
    Args:
        params (dict): 参数字典
            - param1 (type): 参数1说明
            - param2 (type): 参数2说明
    
    Returns:
        dict: 结果字典
            - success (bool): 是否成功
            - result (any): 结果数据
            - error (str): 错误信息（可选）
    
    Example:
        >>> tool_name({'param1': 'value1'})
        {'success': True, 'result': 'output'}
    """
    try:
        # 参数验证
        if 'required_param' not in params:
            return {
                'success': False,
                'error': '缺少必需参数: required_param'
            }
        
        # 业务逻辑
        result = do_something(params)
        
        # 返回结果
        return {
            'success': True,
            'result': result
        }
        
    except Exception as e:
        # 错误处理
        return {
            'success': False,
            'error': str(e)
        }
```

### 3. 参数验证

```python
def validate_params(params, required_keys, optional_keys=None):
    """
    参数验证辅助函数
    """
    # 检查必需参数
    for key in required_keys:
        if key not in params:
            raise ValueError(f'缺少必需参数: {key}')
    
    # 检查参数类型
    if optional_keys:
        for key in params:
            if key not in required_keys and key not in optional_keys:
                raise ValueError(f'未知参数: {key}')
    
    return True


def example_tool(params):
    try:
        validate_params(params, required_keys=['text'], optional_keys=['format'])
        # ... 业务逻辑
    except ValueError as e:
        return {'success': False, 'error': str(e)}
```

### 4. 错误处理

```python
def safe_tool(params):
    """
    安全的工具调用，包含完整错误处理
    """
    try:
        # 1. 参数验证
        if 'input' not in params:
            return {
                'success': False,
                'error': '缺少 input 参数',
                'error_type': 'validation'
            }
        
        # 2. 业务逻辑
        result = process(params['input'])
        
        # 3. 结果验证
        if result is None:
            return {
                'success': False,
                'error': '处理失败，结果为空',
                'error_type': 'processing'
            }
        
        # 4. 成功返回
        return {
            'success': True,
            'result': result,
            'metadata': {
                'processed_at': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        
    except ValueError as e:
        return {
            'success': False,
            'error': f'参数错误: {str(e)}',
            'error_type': 'validation'
        }
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': f'系统错误: {str(e)}',
            'error_type': 'system',
            'traceback': traceback.format_exc()  # 仅调试时使用
        }
```

### 5. Schema 设计

```json
{
    "tool_name": {
        "name": "tool_name",
        "description": "工具的简短描述（一句话）",
        "category": "工具类别（datetime/math/string等）",
        "version": "1.0",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string|number|boolean|array|object",
                    "description": "参数描述",
                    "default": "默认值（可选）",
                    "enum": ["选项1", "选项2"],
                    "minimum": 0,
                    "maximum": 100
                }
            },
            "required": ["param1"],
            "additionalProperties": false
        },
        "returns": {
            "type": "object",
            "description": "返回值描述"
        },
        "examples": [
            {
                "input": {"param1": "value1"},
                "output": {"success": true, "result": "output1"}
            }
        ]
    }
}
```

---

## 示例：完整的工具开发

### 示例 1: 文件工具

**文件**: `builtin_tools/file_tools.py`

```python
"""
文件操作工具集
"""

import os
import json
from pathlib import Path

def file_read(params):
    """
    读取文件内容
    
    Args:
        params (dict):
            - path (str): 文件路径
            - encoding (str): 编码（默认 utf-8）
    
    Returns:
        dict: 包含文件内容的结果
    """
    try:
        path = params.get('path')
        encoding = params.get('encoding', 'utf-8')
        
        if not path:
            return {'success': False, 'error': '缺少 path 参数'}
        
        # 安全检查：只允许读取特定目录
        allowed_dir = '/mnt/zhizhu/mobile-agent/data'
        abs_path = os.path.abspath(path)
        if not abs_path.startswith(allowed_dir):
            return {
                'success': False,
                'error': f'不允许访问目录: {abs_path}'
            }
        
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        
        return {
            'success': True,
            'result': {
                'content': content,
                'size': len(content),
                'lines': content.count('\n') + 1
            }
        }
        
    except FileNotFoundError:
        return {'success': False, 'error': f'文件不存在: {path}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def file_list(params):
    """
    列出目录中的文件
    """
    try:
        path = params.get('path', '.')
        pattern = params.get('pattern', '*')
        
        files = []
        for p in Path(path).glob(pattern):
            files.append({
                'name': p.name,
                'path': str(p),
                'is_dir': p.is_dir(),
                'size': p.stat().st_size if p.is_file() else 0
            })
        
        return {
            'success': True,
            'result': {
                'files': files,
                'count': len(files)
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

**Schema**: 在 `schemas.json` 中添加

```json
{
    "file_read": {
        "name": "file_read",
        "description": "读取文件内容",
        "category": "file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "encoding": {
                    "type": "string",
                    "description": "文件编码",
                    "default": "utf-8",
                    "enum": ["utf-8", "gbk", "ascii"]
                }
            },
            "required": ["path"]
        }
    },
    "file_list": {
        "name": "file_list",
        "description": "列出目录中的文件",
        "category": "file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "目录路径",
                    "default": "."
                },
                "pattern": {
                    "type": "string",
                    "description": "文件匹配模式（glob）",
                    "default": "*"
                }
            }
        }
    }
}
```

### 示例 2: 数据处理工具

**文件**: `builtin_tools/data_tools.py`

```python
"""
数据处理工具集
"""

import json
import csv
from io import StringIO

def json_parse(params):
    """解析 JSON 字符串"""
    try:
        json_str = params.get('json_string', '')
        result = json.loads(json_str)
        return {'success': True, 'result': result}
    except json.JSONDecodeError as e:
        return {'success': False, 'error': f'JSON 解析错误: {str(e)}'}


def json_stringify(params):
    """将对象转换为 JSON 字符串"""
    try:
        data = params.get('data')
        indent = params.get('indent', 2)
        json_str = json.dumps(data, indent=indent, ensure_ascii=False)
        return {'success': True, 'result': json_str}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def csv_to_json(params):
    """将 CSV 转换为 JSON"""
    try:
        csv_str = params.get('csv_string', '')
        delimiter = params.get('delimiter', ',')
        
        reader = csv.DictReader(StringIO(csv_str), delimiter=delimiter)
        result = list(reader)
        
        return {
            'success': True,
            'result': {
                'data': result,
                'count': len(result)
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

---

## 工具测试

### 单元测试

**文件**: `tests/test_builtin_tools.py`

```python
"""
Built-in 工具单元测试
"""

import pytest
from builtin_tools.string_tools import string_reverse, string_to_upper

def test_string_reverse():
    """测试字符串反转"""
    result = string_reverse({'text': 'hello'})
    assert result['success'] == True
    assert result['result'] == 'olleh'
    
def test_string_reverse_empty():
    """测试空字符串反转"""
    result = string_reverse({'text': ''})
    assert result['success'] == True
    assert result['result'] == ''

def test_string_to_upper():
    """测试转大写"""
    result = string_to_upper({'text': 'hello'})
    assert result['success'] == True
    assert result['result'] == 'HELLO'
```

运行测试:
```bash
pytest tests/test_builtin_tools.py -v
```

### 集成测试

**文件**: `test_builtin_integration.py`

```python
"""
Built-in 工具集成测试
"""

import requests

def test_builtin_tools_api():
    """测试 Built-in 工具 API"""
    # 1. 获取工具列表
    resp = requests.get('http://localhost:5000/api/tools/builtin')
    assert resp.status_code == 200
    data = resp.json()
    assert data['success'] == True
    assert len(data['tools']) > 0
    
def test_tool_execution():
    """测试工具执行"""
    # 2. 执行工具
    resp = requests.post('http://localhost:5000/api/tools/execute', json={
        'tool_name': 'string_reverse',
        'parameters': {'text': 'hello'}
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data['success'] == True
    assert data['result'] == 'olleh'
```

---

## 常见问题

### Q1: 如何调试工具？

**方法 1**: 使用 print 调试
```python
def my_tool(params):
    print(f"调试: 收到参数 {params}")
    result = process(params)
    print(f"调试: 结果 {result}")
    return {'success': True, 'result': result}
```

**方法 2**: 使用日志
```python
import logging

logger = logging.getLogger(__name__)

def my_tool(params):
    logger.info(f"工具调用: {params}")
    try:
        result = process(params)
        logger.info(f"工具成功: {result}")
        return {'success': True, 'result': result}
    except Exception as e:
        logger.error(f"工具失败: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}
```

### Q2: 如何处理耗时操作？

使用异步或后台任务:
```python
from threading import Thread

def long_running_tool(params):
    """耗时工具"""
    task_id = generate_task_id()
    
    def background_task():
        result = do_heavy_work(params)
        save_result(task_id, result)
    
    Thread(target=background_task).start()
    
    return {
        'success': True,
        'task_id': task_id,
        'status': 'processing',
        'message': '任务已提交，请稍后查询结果'
    }
```

### Q3: 如何限制工具权限？

```python
def secure_tool(params):
    """安全的工具调用"""
    # 1. 检查调用者权限（需要在 app.py 中实现认证）
    # user = get_current_user()
    # if not user.has_permission('use_secure_tool'):
    #     return {'success': False, 'error': '无权限'}
    
    # 2. 限制参数范围
    allowed_actions = ['read', 'list']
    action = params.get('action')
    if action not in allowed_actions:
        return {'success': False, 'error': f'不允许的操作: {action}'}
    
    # 3. 限制资源访问
    path = params.get('path', '')
    if '..' in path or path.startswith('/'):
        return {'success': False, 'error': '非法路径'}
    
    # 执行安全操作
    return {'success': True, 'result': '...'}
```

### Q4: 如何更新工具而不重启服务？

**选项 1**: 热重载（开发环境）
```python
import importlib

def reload_tools():
    """重新加载所有工具"""
    from builtin_tools import load_tools
    importlib.reload(load_tools)
    return {'success': True, 'message': '工具已重新加载'}
```

**选项 2**: 使用自定义工具（生产环境）
- 对于需要频繁更新的工具，使用页面配置的自定义工具
- Built-in 工具保留给稳定的核心功能

### Q5: 如何组织大量工具？

**推荐结构**:
```
builtin_tools/
├── __init__.py
├── schemas.json
├── core/                   # 核心工具
│   ├── datetime_tools.py
│   ├── math_tools.py
│   └── string_tools.py
├── data/                   # 数据处理
│   ├── json_tools.py
│   ├── csv_tools.py
│   └── xml_tools.py
├── system/                 # 系统工具
│   ├── file_tools.py
│   └── process_tools.py
└── external/               # 外部API集成
    ├── weather_tools.py
    └── search_tools.py
```

---

## 📚 相关文档

- **工具 API 文档**: `TOOL_API.md`
- **快速入门**: `QUICKSTART_TOOLS.md`
- **MCP 指南**: `MCP_GUIDE.md`
- **自动工具解析**: `AUTO_TOOL_PARSE.md`

---

## 🎯 下一步

1. ✅ 查看现有 Built-in 工具: `app.py` 第 305-360 行
2. ✅ 创建你的第一个工具: 参考[快速开始](#快速开始)
3. ✅ 编写测试: 参考[工具测试](#工具测试)
4. ✅ 部署和验证

---

**版本**: v1.0  
**更新日期**: 2024-12-03  
**维护者**: Development Team

