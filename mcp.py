"""
Model Context Protocol (MCP) - 工具调用协调器
负责模型与工具之间的交互协调，支持多轮工具调用循环
"""

import json
import re
import traceback
from typing import Dict, List, Any, Optional, Generator
from datetime import datetime


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
        current_messages = messages.copy()
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
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
        支持多种格式
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
        
        # 格式2: <tool_call name="..." arguments='...'/>
        regex2 = r'<tool_call\s+name="([^"]+)"\s+arguments=\'([^\']+)\'\s*/>'
        for match in re.finditer(regex2, content):
            try:
                args = json.loads(match.group(2))
                tool_calls.append({
                    'name': match.group(1),
                    'arguments': args
                })
            except json.JSONDecodeError:
                pass
        
        # 格式3: 函数调用格式（在</think>后）
        think_end_idx = content.rfind('</think>')
        if think_end_idx != -1:
            after_think = content[think_end_idx + 8:]
            regex3 = r'(\w+)\s*\(\s*({[\s\S]*?})\s*\)'
            for match in re.finditer(regex3, after_think):
                try:
                    args = json.loads(match.group(2))
                    tool_calls.append({
                        'name': match.group(1),
                        'arguments': args
                    })
                except json.JSONDecodeError:
                    pass
        
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

