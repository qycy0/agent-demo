"""
Model Context Protocol (MCP) - 工具调用协调器
负责模型与工具之间的交互协调，支持多轮工具调用循环
"""

import json
import re
import traceback
import logging
from typing import Dict, List, Any, Optional, Generator
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)


class MCPCoordinator:
    """MCP协调器 - 管理模型和工具之间的交互"""
    
    def __init__(self, model_caller, tool_executor):
        """
        初始化MCP协调器
        
        Args:
            model_caller: 模型调用函数
            tool_executor: 工具执行函数
        """
        self.model_caller = model_caller
        self.tool_executor = tool_executor
        self.max_iterations = 10  # 最大工具调用轮数
    
    def coordinate_stream(
        self,
        messages: List[Dict],
        tools: List[Dict],
        params: Dict,
        auto_parse: bool = False
    ) -> Generator:
        """
        协调模型和工具的交互（流式）
        
        Args:
            messages: 对话消息列表
            tools: 可用工具列表
            params: 模型参数
            auto_parse: 是否自动解析工具调用
            
        Yields:
            MCP事件流
        """
        logger.info(f"🔄 MCP协调开始")
        logger.debug(f"   消息数量: {len(messages)}")
        logger.debug(f"   工具数量: {len(tools)}")
        logger.debug(f"   自动解析: {auto_parse}")
        logger.debug(f"   最大迭代: {self.max_iterations}")
        
        current_messages = messages.copy()
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            logger.info(f"   🔁 第 {iteration} 轮迭代开始")
            
            # 发送迭代开始事件
            yield self._create_event('iteration_start', {
                'iteration': iteration,
                'total_messages': len(current_messages)
            })
            
            # 调用模型（流式）
            model_content = ''
            thinking_content = ''
            has_tool_calls = False
            tool_calls = []
            
            # 发送thinking状态
            yield self._create_event('status', {'status': 'thinking'})
            
            try:
                # 收集模型的完整输出
                for chunk in self.model_caller(current_messages, tools, params):
                    if chunk['type'] == 'content':
                        model_content += chunk['content']
                        # 实时传递内容
                        yield chunk
                    elif chunk['type'] == 'status':
                        yield chunk
                    elif chunk['type'] == 'error':
                        yield chunk
                        return
                    elif chunk['type'] == 'done':
                        # 先不发送done，等工具调用完成
                        pass
                
                # 解析thinking内容
                thinking_content = self._extract_thinking(model_content)
                if thinking_content:
                    yield self._create_event('thinking_extracted', {
                        'thinking': thinking_content
                    })
                
                # 如果启用自动解析，从输出中提取工具调用
                if auto_parse:
                    tool_calls = self._parse_tool_calls(model_content)
                    if tool_calls:
                        has_tool_calls = True
                        yield self._create_event('tool_calls_parsed', {
                            'count': len(tool_calls),
                            'calls': tool_calls
                        })
                
                # 如果没有工具调用，结束循环
                if not has_tool_calls:
                    # 添加助手消息到历史
                    current_messages.append({
                        'role': 'assistant',
                        'content': self._clean_content(model_content)
                    })
                    
                    yield self._create_event('iteration_complete', {
                        'iteration': iteration,
                        'has_tool_calls': False
                    })
                    
                    # 发送最终done
                    yield self._create_event('done', {})
                    break
                
                # 执行工具调用
                yield self._create_event('status', {'status': 'function_calling'})
                
                tool_results = []
                for tool_call in tool_calls:
                    logger.info(f"      🔧 执行工具: {tool_call['name']}")
                    logger.debug(f"         参数: {json.dumps(tool_call['arguments'], ensure_ascii=False)}")
                    
                    # 发送工具调用开始事件
                    yield self._create_event('tool_call_start', {
                        'name': tool_call['name'],
                        'arguments': tool_call['arguments']
                    })
                    
                    try:
                        # 执行工具
                        result = self.tool_executor(
                            tool_call['name'],
                            tool_call['arguments']
                        )
                        
                        logger.info(f"         ✅ 工具执行成功")
                        logger.debug(f"         结果: {json.dumps(result, ensure_ascii=False)[:300]}")
                        
                        tool_results.append({
                            'name': tool_call['name'],
                            'arguments': tool_call['arguments'],
                            'result': result,
                            'success': result.get('success', False)
                        })
                        
                        # 发送工具调用完成事件
                        yield self._create_event('tool_call_complete', {
                            'name': tool_call['name'],
                            'success': result.get('success', False),
                            'result': result
                        })
                        
                    except Exception as e:
                        error_result = {
                            'success': False,
                            'error': str(e)
                        }
                        
                        tool_results.append({
                            'name': tool_call['name'],
                            'arguments': tool_call['arguments'],
                            'result': error_result,
                            'success': False
                        })
                        
                        yield self._create_event('tool_call_error', {
                            'name': tool_call['name'],
                            'error': str(e)
                        })
                
                # 将模型输出添加到消息历史（只保留清理后的内容，不包含工具调用）
                assistant_content = self._clean_content(model_content)
                current_messages.append({
                    'role': 'assistant',
                    'content': assistant_content if assistant_content else '我需要使用工具来回答这个问题。'
                })
                
                # 添加工具结果到消息 - 格式化为易于模型理解的形式
                tool_results_summary = []
                for tool_result in tool_results:
                    result_str = json.dumps(tool_result['result'], ensure_ascii=False, indent=2)
                    if tool_result['success']:
                        tool_results_summary.append(
                            f"工具 {tool_result['name']} 执行成功，结果：\n{result_str}"
                        )
                    else:
                        tool_results_summary.append(
                            f"工具 {tool_result['name']} 执行失败，错误：{tool_result['result'].get('error', '未知错误')}"
                        )
                
                # 将工具结果作为一条消息添加
                if tool_results_summary:
                    current_messages.append({
                        'role': 'user',
                        'content': f"以下是工具执行的结果，请基于这些结果回答我的问题：\n\n" + '\n\n'.join(tool_results_summary)
                    })
                
                # 发送迭代完成事件
                yield self._create_event('iteration_complete', {
                    'iteration': iteration,
                    'has_tool_calls': True,
                    'tool_results': tool_results
                })
                
                # 继续下一轮迭代（让模型处理工具结果）
                
            except Exception as e:
                traceback.print_exc()
                # 发送错误状态和错误事件
                yield self._create_event('status', {'status': 'error'})
                yield self._create_event('error', {
                    'error': f'MCP协调错误: {str(e)}'
                })
                yield self._create_event('done', {})
                break
        
        # 如果达到最大迭代次数
        if iteration >= self.max_iterations:
            yield self._create_event('max_iterations_reached', {
                'max_iterations': self.max_iterations
            })
            yield self._create_event('done', {})
    
    def _extract_thinking(self, content: str) -> str:
        """提取thinking内容"""
        think_regex = r'<think>([\s\S]*?)</think>'
        matches = re.findall(think_regex, content)
        if matches:
            return '\n'.join(matches)
        return ''
    
    def _clean_content(self, content: str) -> str:
        """清理内容，移除thinking和工具调用标签"""
        # 移除thinking标签
        content = re.sub(r'<think>[\s\S]*?</think>', '', content)
        
        # 移除格式1: <tool_call>...</tool_call>
        content = re.sub(r'<tool_call>[\s\S]*?</tool_call>', '', content)
        
        # 移除格式2: <tool_call ... />
        content = re.sub(r'<tool_call[^>]*?/>', '', content)
        
        # 移除格式3: 函数调用格式 function_name({...})
        # 先找到</think>之后的内容
        think_end_idx = content.rfind('</think>')
        if think_end_idx != -1:
            before_think = content[:think_end_idx + 8]
            after_think = content[think_end_idx + 8:]
            # 移除函数调用
            after_think = re.sub(r'\w+\s*\(\s*\{[\s\S]*?\}\s*\)', '', after_think)
            content = before_think + after_think
        else:
            # 如果没有think标签，也尝试移除函数调用
            content = re.sub(r'\w+\s*\(\s*\{[\s\S]*?\}\s*\)', '', content)
        
        return content.strip()
    
    def _parse_tool_calls(self, content: str) -> List[Dict]:
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
        # 查找最后一个<tool_call>，如果没有对应的</tool_call>，尝试解析
        last_open_tag_idx = content.rfind('<tool_call>')
        if last_open_tag_idx != -1:
            # 检查这个<tool_call>是否已经被format1处理
            after_last_open = content[last_open_tag_idx:]
            if '</tool_call>' not in after_last_open:
                # 未封闭的tool_call，尝试提取内容
                json_content = after_last_open[11:].strip()  # 11 = len('<tool_call>')
                
                # 尝试多种JSON提取策略
                # 策略1: 直接解析（可能完整）
                try:
                    call_data = json.loads(json_content)
                    if 'name' in call_data and call_data['name'] not in [t['name'] for t in tool_calls]:
                        tool_calls.append({
                            'name': call_data['name'],
                            'arguments': call_data.get('arguments', {})
                        })
                except json.JSONDecodeError:
                    # 策略2: 尝试找到JSON的部分（可能被截断）
                    # 查找可能的JSON结构（可能不完整）
                    json_match = re.search(r'(\{[\s\S]*)', json_content)
                    if json_match:
                        potential_json = json_match.group(1)
                        # 尝试多种补全方式
                        # 注意：被截断的JSON可能是：{"name":"tool","argu
                        # 我们需要补全成：{"name":"tool","arguments":{}} 或 {"name":"tool"}
                        attempts = [
                            potential_json,          # 原样
                            potential_json + '}',    # 补一个右括号
                            potential_json + '}}',   # 补两个右括号
                            potential_json + '""}',  # 补引号和括号
                            potential_json + '":""}', # 补完整的键值对
                        ]
                        
                        # 如果看起来是被截断的键（如 "argu），尝试移除它
                        if re.search(r'[,\{]\s*"[^"]*$', potential_json):
                            # 移除最后不完整的键
                            cleaned = re.sub(r'[,\{]\s*"[^"]*$', '', potential_json)
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
        
        # 格式2b: 未封闭的属性格式 <tool_call name="..." (可能未完成)
        regex2b = r'<tool_call\s+name="([^"]+)"(?:\s+arguments=[\'"]([^\'"]*)[\'"]?)?(?!/>)'
        for match in re.finditer(regex2b, content):
            tool_name = match.group(1)
            if tool_name not in [t['name'] for t in tool_calls]:
                args_str = match.group(2) if match.group(2) else '{}'
                try:
                    # 尝试解析参数
                    args = json.loads(args_str) if args_str else {}
                    tool_calls.append({
                        'name': tool_name,
                        'arguments': args
                    })
                except json.JSONDecodeError:
                    # 参数解析失败，使用空参数
                    tool_calls.append({
                        'name': tool_name,
                        'arguments': {}
                    })
        
        # 格式3: 函数调用格式（在</think>后或整个内容中）
        # 先尝试</think>之后
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
        
        # 格式3b: 未封闭的函数调用 function_name({...  （没有闭合括号）
        regex3b = r'(\w+)\s*\(\s*(\{[\s\S]*?)$'
        for match in re.finditer(regex3b, search_area):
            func_name = match.group(1)
            # 避免误匹配普通文本，检查是否真的像工具调用
            if func_name.islower() or '_' in func_name:  # 工具名通常是小写或包含下划线
                if func_name not in [t['name'] for t in tool_calls]:
                    json_part = match.group(2).strip()
                    # 尝试补全JSON
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
    
    def _create_event(self, event_type: str, data: Dict = None) -> Dict:
        """创建MCP事件"""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            event.update(data)
        return event


def format_mcp_event_for_sse(event: Dict) -> str:
    """将MCP事件格式化为SSE格式"""
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

