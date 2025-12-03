#!/usr/bin/env python3
"""
工具功能测试脚本
演示如何使用工具API
"""

import requests
import json

API_BASE = 'http://localhost:5000'

def test_builtin_tools():
    """测试内置工具"""
    print("=== 测试内置工具列表 ===")
    response = requests.get(f'{API_BASE}/api/tools/builtin')
    data = response.json()
    if data['success']:
        print(f"✓ 找到 {len(data['tools'])} 个内置工具:")
        for tool in data['tools']:
            print(f"  - {tool['name']}: {tool['description']}")
    else:
        print("✗ 获取内置工具失败")
    print()

def test_calculate_tool():
    """测试计算器工具"""
    print("=== 测试计算器工具 ===")
    response = requests.post(f'{API_BASE}/api/tools/execute', json={
        'tool_name': 'calculate',
        'parameters': {
            'expression': '2 + 3 * 4'
        }
    })
    data = response.json()
    if data.get('success'):
        print(f"✓ 计算结果: {data['result']['expression']} = {data['result']['value']}")
    else:
        print(f"✗ 计算失败: {data.get('error')}")
    print()

def test_time_tool():
    """测试时间工具"""
    print("=== 测试时间工具 ===")
    response = requests.post(f'{API_BASE}/api/tools/execute', json={
        'tool_name': 'get_current_time',
        'parameters': {
            'timezone': 'Asia/Shanghai'
        }
    })
    data = response.json()
    if data.get('success'):
        print(f"✓ 当前时间: {data['result']['time']}")
        print(f"  时区: {data['result']['timezone']}")
        print(f"  时间戳: {data['result']['timestamp']}")
    else:
        print(f"✗ 获取时间失败: {data.get('error')}")
    print()

def register_custom_tool():
    """注册自定义工具示例"""
    print("=== 注册自定义文本工具 ===")
    response = requests.post(f'{API_BASE}/api/tools/register', json={
        'name': 'text_analyzer',
        'description': '分析文本的长度和单词数',
        'tool_type': 'code',
        'parameters': {
            'type': 'object',
            'properties': {
                'text': {
                    'type': 'string',
                    'description': '要分析的文本'
                }
            },
            'required': ['text']
        },
        'code': '''
text = params.get('text', '')
words = text.split()
result = {
    'length': len(text),
    'words': len(words),
    'uppercase': text.upper()
}
'''
    })
    data = response.json()
    if data.get('success'):
        print(f"✓ 工具注册成功: {data['tool']['name']}")
        print(f"  ID: {data['tool']['id']}")
        return data['tool']['id']
    else:
        print(f"✗ 工具注册失败: {data.get('error')}")
        return None
    print()

def test_custom_tool():
    """测试自定义工具"""
    print("=== 测试自定义工具 ===")
    
    # 先注册
    tool_id = register_custom_tool()
    if not tool_id:
        return
    
    # 执行工具
    response = requests.post(f'{API_BASE}/api/tools/execute', json={
        'tool_name': 'text_analyzer',
        'parameters': {
            'text': 'Hello World from Tool API'
        }
    })
    data = response.json()
    if data.get('success'):
        print(f"✓ 文本分析结果:")
        print(f"  长度: {data['result']['length']}")
        print(f"  单词数: {data['result']['words']}")
        print(f"  大写: {data['result']['uppercase']}")
    else:
        print(f"✗ 执行失败: {data.get('error')}")
    
    # 清理：删除测试工具
    requests.delete(f'{API_BASE}/api/tools/{tool_id}')
    print()

def test_register_api_tool():
    """演示注册外部API工具"""
    print("=== 注册外部API工具示例 ===")
    tool_config = {
        'name': 'weather_api',
        'description': '查询天气信息',
        'tool_type': 'api',
        'api_url': 'https://api.openweathermap.org/data/2.5/weather',
        'api_method': 'GET',
        'api_headers': {
            'Content-Type': 'application/json'
        },
        'parameters': {
            'type': 'object',
            'properties': {
                'city': {
                    'type': 'string',
                    'description': '城市名称'
                },
                'appid': {
                    'type': 'string',
                    'description': 'API密钥'
                }
            },
            'required': ['city', 'appid']
        }
    }
    print("配置示例:")
    print(json.dumps(tool_config, indent=2, ensure_ascii=False))
    print("\n注意: 这只是配置示例，需要真实的API密钥才能实际使用")
    print()

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("行业智能通用运维模型2.0 - 工具API测试")
    print("="*60 + "\n")
    
    try:
        # 测试基础功能
        test_builtin_tools()
        test_calculate_tool()
        test_time_tool()
        
        # 测试自定义工具
        test_custom_tool()
        
        # 演示API工具配置
        test_register_api_tool()
        
        print("="*60)
        print("✓ 所有测试完成")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到服务器")
        print("请确保服务器正在运行: python app.py")
    except Exception as e:
        print(f"\n✗ 测试过程中出错: {e}")

if __name__ == '__main__':
    main()

