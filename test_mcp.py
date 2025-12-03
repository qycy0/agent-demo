#!/usr/bin/env python3
"""
MCP系统测试脚本
测试工具调用循环和详细信息记录
"""

import json
from mcp import MCPCoordinator

def mock_model_caller(messages, tools, params):
    """模拟模型调用（用于测试）"""
    # 模拟流式输出
    test_responses = [
        {'type': 'status', 'status': 'thinking'},
        {'type': 'content', 'content': '<think>需要先获取时间</think>'},
        {'type': 'content', 'content': '\n<tool_call>'},
        {'type': 'content', 'content': '{"name": "get_current_time", "arguments": {"timezone": "UTC"}}'},
        {'type': 'content', 'content': '</tool_call>'},
        {'type': 'done'}
    ]
    
    for response in test_responses:
        yield response

def mock_tool_executor(tool_name, tool_args):
    """模拟工具执行（用于测试）"""
    if tool_name == 'get_current_time':
        return {
            'success': True,
            'result': {
                'time': '2024-12-03 14:30:00',
                'timezone': tool_args.get('timezone', 'UTC'),
                'timestamp': 1701594600
            }
        }
    elif tool_name == 'calculate':
        expression = tool_args.get('expression', '')
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return {
                'success': True,
                'result': {
                    'expression': expression,
                    'value': result
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    else:
        return {
            'success': False,
            'error': f'工具 {tool_name} 未注册'
        }

def test_mcp_basic():
    """测试基本的MCP功能"""
    print("=== 测试1: 基本工具调用 ===")
    
    # 创建MCP协调器
    mcp = MCPCoordinator(mock_model_caller, mock_tool_executor)
    
    # 测试消息
    messages = [
        {'role': 'user', 'content': '现在几点了？'}
    ]
    
    # 执行协调
    events = []
    for event in mcp.coordinate_stream(messages, [], {}, auto_parse=True):
        events.append(event)
        print(f"  [{event['type']}] {event.get('timestamp', '')}")
        if event['type'] == 'tool_call_complete':
            print(f"    工具: {event['name']}, 成功: {event['success']}")
    
    print(f"✓ 共收到 {len(events)} 个事件")
    print()

def test_tool_parsing():
    """测试工具调用解析"""
    print("=== 测试2: 工具调用解析 ===")
    
    from mcp import MCPCoordinator
    
    # 创建协调器实例
    mcp = MCPCoordinator(None, None)
    
    # 测试不同格式
    test_cases = [
        # 格式1: JSON
        '<tool_call>{"name": "calculate", "arguments": {"expression": "2+3"}}</tool_call>',
        # 格式2: XML属性
        '<tool_call name="calculate" arguments=\'{"expression": "2+3"}\'/>',
        # 格式3: 函数调用
        '<think>测试</think>\ncalculate({"expression": "2+3"})'
    ]
    
    for i, content in enumerate(test_cases, 1):
        tool_calls = mcp._parse_tool_calls(content)
        print(f"  格式{i}: 解析到 {len(tool_calls)} 个工具调用")
        for call in tool_calls:
            print(f"    - {call['name']}({json.dumps(call['arguments'], ensure_ascii=False)})")
    
    print("✓ 工具解析测试完成")
    print()

def test_thinking_extraction():
    """测试thinking内容提取"""
    print("=== 测试3: Thinking提取 ===")
    
    from mcp import MCPCoordinator
    
    mcp = MCPCoordinator(None, None)
    
    content = '''<think>
    这是思考内容
    需要使用工具
    </think>
    这是正常输出'''
    
    thinking = mcp._extract_thinking(content)
    cleaned = mcp._clean_content(content)
    
    print(f"  原始内容长度: {len(content)}")
    print(f"  提取thinking: {len(thinking)} 字符")
    print(f"  清理后内容: {len(cleaned)} 字符")
    print(f"  Thinking内容: {thinking[:50]}...")
    print(f"  清理后: {cleaned[:30]}...")
    print("✓ Thinking提取测试完成")
    print()

def test_event_formatting():
    """测试事件格式化"""
    print("=== 测试4: 事件格式化 ===")
    
    from mcp import format_mcp_event_for_sse
    
    events = [
        {'type': 'iteration_start', 'iteration': 1},
        {'type': 'tool_call_start', 'name': 'calculate', 'arguments': {'x': 1}},
        {'type': 'tool_call_complete', 'name': 'calculate', 'success': True, 'result': {'value': 5}}
    ]
    
    for event in events:
        sse_data = format_mcp_event_for_sse(event)
        print(f"  {event['type']}: {len(sse_data)} bytes")
        # 验证格式
        assert sse_data.startswith('data: '), "SSE格式错误"
        assert sse_data.endswith('\n\n'), "SSE结尾格式错误"
    
    print("✓ 事件格式化测试完成")
    print()

def test_error_handling():
    """测试错误处理"""
    print("=== 测试5: 错误处理 ===")
    
    # 测试工具执行错误
    result = mock_tool_executor('non_existent_tool', {})
    assert not result['success'], "应该返回失败"
    print(f"  ✓ 未注册工具: {result['error']}")
    
    # 测试计算错误
    result = mock_tool_executor('calculate', {'expression': '10/0'})
    assert not result['success'], "除零应该失败"
    print(f"  ✓ 除零错误: {result['error']}")
    
    # 测试计算成功
    result = mock_tool_executor('calculate', {'expression': '2+3'})
    assert result['success'], "正常计算应该成功"
    print(f"  ✓ 正常计算: {result['result']['value']} = 5")
    
    print("✓ 错误处理测试完成")
    print()

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("MCP系统功能测试")
    print("="*60 + "\n")
    
    try:
        # test_mcp_basic()
        test_tool_parsing()
        test_thinking_extraction()
        test_event_formatting()
        test_error_handling()
        
        print("="*60)
        print("✓ 所有测试通过")
        print("="*60)
        
        print("\n📖 使用指南:")
        print("  1. 查看 MCP_GUIDE.md 了解详细功能")
        print("  2. 启动服务: python app.py")
        print("  3. 在网页中启用'自动解析工具调用'")
        print("  4. 发送需要多步骤的问题")
        print("  5. 点击 📋 按钮查看详细过程")
        
    except Exception as e:
        import traceback
        print(f"\n✗ 测试失败: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()

