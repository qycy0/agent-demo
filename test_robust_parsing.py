#!/usr/bin/env python3
"""
测试MCP工具调用解析的鲁棒性
验证各种边缘情况和不完整输出
"""

import re
import json
from typing import List, Dict

def _parse_tool_calls(content: str) -> List[Dict]:
    """
    从模型输出中解析工具调用
    支持多种格式，具有鲁棒性处理
    """
    tool_calls = []
    
    # 格式1: <tool_call>{"name": "...", "arguments": {...}}</tool_call>
    regex1 = r'<tool_call>([\s\S]*?)</tool_call>'
    for match in re.finditer(regex1, content):
        try:
            call_data = json.loads(match.group(1).strip())
            if 'name' in call_data:
                tool_calls.append({
                    'name': call_data['name'],
                    'arguments': call_data.get('arguments', {})
                })
        except json.JSONDecodeError:
            pass
    
    # 格式1b: 未封闭的<tool_call>（流式输出时可能出现）
    last_open_tag_idx = content.rfind('<tool_call>')
    if last_open_tag_idx != -1:
        after_last_open = content[last_open_tag_idx:]
        if '</tool_call>' not in after_last_open:
            json_content = after_last_open[11:].strip()
            
            # 策略1: 直接解析
            try:
                call_data = json.loads(json_content)
                if 'name' in call_data and call_data['name'] not in [t['name'] for t in tool_calls]:
                    tool_calls.append({
                        'name': call_data['name'],
                        'arguments': call_data.get('arguments', {})
                    })
            except json.JSONDecodeError:
                # 策略2: 尝试找到JSON的部分（可能被截断）
                json_match = re.search(r'(\{[\s\S]*)', json_content)
                if json_match:
                    potential_json = json_match.group(1)
                    # 尝试多种补全方式
                    attempts = [
                        potential_json,
                        potential_json + '}',
                        potential_json + '}}',
                        potential_json + '""}',
                        potential_json + '":""}',
                    ]
                    
                    # 如果看起来是被截断的键（如 "argu），尝试移除它
                    if re.search(r'[,\{]\s*"[^"]*$', potential_json):
                        cleaned = re.sub(r',\s*"[^"]*$', '', potential_json)
                        attempts.extend([
                            cleaned + '}',
                            cleaned + '}}',
                        ])
                    
                    for attempt in attempts:
                        try:
                            call_data = json.loads(attempt)
                            if 'name' in call_data and call_data['name'] not in [t['name'] for t in tool_calls]:
                                tool_calls.append({
                                    'name': call_data['name'],
                                    'arguments': call_data.get('arguments', {})
                                })
                                break
                        except json.JSONDecodeError:
                            continue
    
    # 格式2: <tool_call name="..." arguments='...'/>
    regex2 = r'<tool_call\s+name="([^"]+)"\s+arguments=\'([^\']+)\'\s*/>'
    for match in re.finditer(regex2, content):
        try:
            args = json.loads(match.group(2))
            if match.group(1) not in [t['name'] for t in tool_calls]:
                tool_calls.append({
                    'name': match.group(1),
                    'arguments': args
                })
        except json.JSONDecodeError:
            pass
    
    # 格式2b: 未封闭的属性格式
    regex2b = r'<tool_call\s+name="([^"]+)"(?:\s+arguments=[\'"]([^\'"]*)[\'"]?)?(?!/>)'
    for match in re.finditer(regex2b, content):
        tool_name = match.group(1)
        if tool_name not in [t['name'] for t in tool_calls]:
            args_str = match.group(2) if match.group(2) else '{}'
            try:
                args = json.loads(args_str) if args_str else {}
                tool_calls.append({
                    'name': tool_name,
                    'arguments': args
                })
            except json.JSONDecodeError:
                tool_calls.append({
                    'name': tool_name,
                    'arguments': {}
                })
    
    # 格式3: 函数调用格式
    think_end_idx = content.rfind('</think>')
    search_area = content[think_end_idx + 8:] if think_end_idx != -1 else content
    
    # 完整的函数调用
    regex3 = r'(\w+)\s*\(\s*(\{[\s\S]*?\})\s*\)'
    for match in re.finditer(regex3, search_area):
        func_name = match.group(1)
        if func_name not in [t['name'] for t in tool_calls]:
            try:
                args = json.loads(match.group(2))
                tool_calls.append({
                    'name': func_name,
                    'arguments': args
                })
            except json.JSONDecodeError:
                pass
    
    # 格式3b: 未封闭的函数调用
    regex3b = r'(\w+)\s*\(\s*(\{[\s\S]*?)$'
    for match in re.finditer(regex3b, search_area):
        func_name = match.group(1)
        if func_name.islower() or '_' in func_name:
            if func_name not in [t['name'] for t in tool_calls]:
                json_part = match.group(2).strip()
                for attempt in [json_part, json_part + '}', json_part + '}}']:
                    try:
                        args = json.loads(attempt)
                        tool_calls.append({
                            'name': func_name,
                            'arguments': args
                        })
                        break
                    except json.JSONDecodeError:
                        continue
    
    return tool_calls

def test_complete_formats():
    """测试完整格式的解析"""
    print("=== 测试1: 完整格式解析 ===")
    
    test_cases = [
        {
            'input': '<think>需要时间</think><tool_call>{"name":"get_time","arguments":{"tz":"UTC"}}</tool_call>',
            'expected': [{'name': 'get_time', 'arguments': {'tz': 'UTC'}}],
            'desc': '格式1: JSON标签'
        },
        {
            'input': '<think>计算</think><tool_call name="calculate" arguments=\'{"expr":"2+3"}\'/> ',
            'expected': [{'name': 'calculate', 'arguments': {'expr': '2+3'}}],
            'desc': '格式2: 属性标签'
        },
        {
            'input': '<think>获取时间</think>get_current_time({"timezone":"Asia/Shanghai"})',
            'expected': [{'name': 'get_current_time', 'arguments': {'timezone': 'Asia/Shanghai'}}],
            'desc': '格式3: 函数调用'
        },
    ]
    
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        result = _parse_tool_calls(test['input'])
        passed = result == test['expected']
        all_passed = all_passed and passed
        
        status = '✅' if passed else '❌'
        print(f"  {status} 测试{i} - {test['desc']}")
        if not passed:
            print(f"      期望: {test['expected']}")
            print(f"      实际: {result}")
    
    print(f"  {'✅ 完整格式测试通过' if all_passed else '❌ 部分测试失败'}\n")
    return all_passed

def test_incomplete_formats():
    """测试不完整格式的解析（鲁棒性测试）"""
    print("=== 测试2: 不完整格式解析（鲁棒性）===")
    
    test_cases = [
        {
            'input': '<think>需要时间</think><tool_call>{"name":"get_time"',
            'expected_name': 'get_time',
            'desc': '未封闭标签 - 只有name'
        },
        {
            'input': '<think>计算</think><tool_call>{"name":"calculate","arguments":{"expr":"2+3"',
            'expected_name': 'calculate',
            'desc': '未封闭标签 - JSON不完整'
        },
        {
            'input': '<think>获取</think><tool_call name="get_data"',
            'expected_name': 'get_data',
            'desc': '属性格式未完成'
        },
        {
            'input': '<think>处理</think>process_data({"key":"value"',
            'expected_name': 'process_data',
            'desc': '函数调用未封闭'
        },
        {
            'input': '<tool_call>{"name":"test_tool","arguments":{}',
            'expected_name': 'test_tool',
            'desc': '无thinking的未封闭标签'
        },
    ]
    
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        result = _parse_tool_calls(test['input'])
        # 检查是否解析出了预期的工具名
        found = any(t['name'] == test['expected_name'] for t in result)
        all_passed = all_passed and found
        
        status = '✅' if found else '❌'
        print(f"  {status} 测试{i} - {test['desc']}")
        if not found:
            print(f"      期望工具: {test['expected_name']}")
            print(f"      解析结果: {result}")
        else:
            print(f"      解析成功: {result}")
    
    print(f"  {'✅ 不完整格式测试通过' if all_passed else '❌ 部分测试失败'}\n")
    return all_passed

def test_edge_cases():
    """测试边缘情况"""
    print("=== 测试3: 边缘情况 ===")
    
    test_cases = [
        {
            'input': '<think>思考</think>答案是42',
            'expected': [],
            'desc': '无工具调用'
        },
        {
            'input': '<tool_call>{"name":"tool1"}</tool_call><tool_call>{"name":"tool2"}</tool_call>',
            'expected_count': 2,
            'desc': '多个工具调用'
        },
        {
            'input': '<think>思考</think><tool_call>invalid json</tool_call>',
            'expected': [],
            'desc': '无效JSON'
        },
        {
            'input': '<tool_call>{"name":"tool1"}</tool_call><tool_call>{"name":"tool1',
            'expected_names': ['tool1'],  # 应该只有一个，去重
            'desc': '重复工具名（去重测试）'
        },
    ]
    
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        result = _parse_tool_calls(test['input'])
        
        if 'expected' in test:
            passed = result == test['expected']
        elif 'expected_count' in test:
            passed = len(result) == test['expected_count']
        elif 'expected_names' in test:
            result_names = [t['name'] for t in result]
            passed = result_names == test['expected_names']
        else:
            passed = False
        
        all_passed = all_passed and passed
        
        status = '✅' if passed else '❌'
        print(f"  {status} 测试{i} - {test['desc']}")
        if not passed:
            print(f"      解析结果: {result}")
    
    print(f"  {'✅ 边缘情况测试通过' if all_passed else '❌ 部分测试失败'}\n")
    return all_passed

def test_streaming_scenarios():
    """测试流式输出场景"""
    print("=== 测试4: 流式输出场景 ===")
    
    # 模拟流式输出的逐步累积
    streaming_steps = [
        '<think>',
        '<think>需要',
        '<think>需要获取时间',
        '<think>需要获取时间</think>',
        '<think>需要获取时间</think><tool',
        '<think>需要获取时间</think><tool_call>',
        '<think>需要获取时间</think><tool_call>{"name"',
        '<think>需要获取时间</think><tool_call>{"name":"get_time"',
        '<think>需要获取时间</think><tool_call>{"name":"get_time","arguments"',
        '<think>需要获取时间</think><tool_call>{"name":"get_time","arguments":{}',
        '<think>需要获取时间</think><tool_call>{"name":"get_time","arguments":{}}</tool_call>',
    ]
    
    print("  模拟流式输出逐步解析:")
    tool_found_at_step = -1
    
    for i, step in enumerate(streaming_steps):
        result = _parse_tool_calls(step)
        if result and tool_found_at_step == -1:
            tool_found_at_step = i
        
        status = '✅' if result else '⏳'
        print(f"    步骤{i+1:2d}: {status} 长度={len(step):3d}, 解析={len(result)} {'← 首次解析成功' if i == tool_found_at_step else ''}")
    
    # 检查是否在合理的步骤就能解析出工具调用
    passed = 0 < tool_found_at_step < len(streaming_steps) - 1
    
    if passed:
        print(f"  ✅ 流式输出在第{tool_found_at_step+1}步成功解析（总共{len(streaming_steps)}步）")
        print(f"     鲁棒性: 在输出完整前{len(streaming_steps)-tool_found_at_step-1}步就能识别\n")
    else:
        print(f"  ❌ 流式输出解析失败\n")
    
    return passed

def test_real_world_examples():
    """测试真实场景示例"""
    print("=== 测试5: 真实场景示例 ===")
    
    test_cases = [
        {
            'input': '''<think>
用户问现在几点，我需要调用时间工具来获取当前时间。
</think>
<tool_call>
{"name": "get_current_time", "arguments": {"timezone": "Asia/Shanghai", "format": "24h"}}
</tool_call>''',
            'expected_name': 'get_current_time',
            'desc': '真实场景1: 多行格式化JSON'
        },
        {
            'input': '<think>需要计算两个数的和</think>calculate({"operation":"add","numbers":[2,3]})',
            'expected_name': 'calculate',
            'desc': '真实场景2: 函数调用格式'
        },
        {
            'input': '''<think>获取天气信息</think><tool_call name="get_weather" arguments='{"city":"Beijing","units":"metric"}'/>然后返回结果''',
            'expected_name': 'get_weather',
            'desc': '真实场景3: 属性格式带后续文本'
        },
        {
            'input': '<think>搜索相关信息</think><tool_call>{"name":"web_search","argu',
            'expected_name': 'web_search',
            'desc': '真实场景4: 流式输出被截断'
        },
    ]
    
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        result = _parse_tool_calls(test['input'])
        found = any(t['name'] == test['expected_name'] for t in result)
        all_passed = all_passed and found
        
        status = '✅' if found else '❌'
        print(f"  {status} 测试{i} - {test['desc']}")
        if found:
            tool = next(t for t in result if t['name'] == test['expected_name'])
            print(f"      工具: {tool['name']}")
            print(f"      参数: {tool['arguments']}")
        else:
            print(f"      期望: {test['expected_name']}")
            print(f"      结果: {result}")
    
    print(f"  {'✅ 真实场景测试通过' if all_passed else '❌ 部分测试失败'}\n")
    return all_passed

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("MCP工具调用解析鲁棒性测试")
    print("="*60 + "\n")
    
    results = []
    
    try:
        results.append(('完整格式', test_complete_formats()))
        results.append(('不完整格式', test_incomplete_formats()))
        results.append(('边缘情况', test_edge_cases()))
        results.append(('流式输出', test_streaming_scenarios()))
        results.append(('真实场景', test_real_world_examples()))
        
        print("="*60)
        print("测试结果汇总")
        print("="*60)
        
        for name, passed in results:
            status = '✅' if passed else '❌'
            print(f"  {status} {name}")
        
        all_passed = all(r[1] for r in results)
        
        if all_passed:
            print("\n" + "="*60)
            print("✅ 所有测试通过 - 工具解析具有良好鲁棒性")
            print("="*60)
            
            print("\n📝 鲁棒性特性:")
            print("  1. ✅ 支持三种完整格式")
            print("  2. ✅ 处理未封闭标签")
            print("  3. ✅ 自动补全不完整JSON")
            print("  4. ✅ 流式输出早期识别")
            print("  5. ✅ 工具名去重")
            print("  6. ✅ 错误输入容错")
            
            print("\n🎯 适用场景:")
            print("  • 流式输出（逐字符生成）")
            print("  • 网络中断（输出截断）")
            print("  • 模型输出不规范")
            print("  • 多种格式混用")
        else:
            print("\n❌ 部分测试失败，请检查实现")
        
    except Exception as e:
        import traceback
        print(f"\n❌ 测试出错: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()

