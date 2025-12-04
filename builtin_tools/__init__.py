"""
Built-in 工具加载器
自动发现和注册所有内置工具
"""

import os
import json
import importlib
import logging
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

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
        module_name = file.stem  # 例如: datetime_tools
        try:
            module = importlib.import_module(f'builtin_tools.{module_name}')
            
            # 获取模块中的所有函数
            for name in dir(module):
                if not name.startswith('_'):  # 忽略私有函数
                    func = getattr(module, name)
                    if callable(func):
                        BUILTIN_TOOLS[name] = func
                        print(f"  ✓ 加载工具: {name}")
        except Exception as e:
            print(f"  ✗ 加载模块 {module_name} 失败: {e}")
    
    print(f"✓ 共加载 {len(BUILTIN_TOOLS)} 个内置工具")
    return BUILTIN_TOOLS, BUILTIN_SCHEMAS


def get_tool(name):
    """获取指定工具"""
    return BUILTIN_TOOLS.get(name)


def get_schema(name):
    """获取工具的 Schema"""
    return BUILTIN_SCHEMAS.get(name)


def list_tools():
    """列出所有工具名称"""
    return list(BUILTIN_TOOLS.keys())


def list_schemas():
    """列出所有 Schema"""
    return list(BUILTIN_SCHEMAS.values())


# 自动加载
print("正在加载 Built-in 工具...")
load_tools()

