"""
行业智能通用运维模型2.0 后端服务
提供模型管理、工具管理和对话功能
"""
import os
import json
import base64
import requests
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import traceback
from mcp import MCPCoordinator, format_mcp_event_for_sse

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 请求日志中间件
@app.before_request
def log_request():
    """记录所有请求"""
    logger.info(f"━━━━ 新请求 ━━━━")
    logger.info(f"Method: {request.method}")
    logger.info(f"Path: {request.path}")
    logger.info(f"IP: {request.remote_addr}")
    if request.args:
        logger.info(f"Query Params: {dict(request.args)}")
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            if request.is_json:
                data = request.get_json()
                # 对于大数据量的请求，只记录摘要
                if isinstance(data, dict):
                    if 'messages' in data:
                        logger.info(f"Request Data: messages=[{len(data['messages'])} items], ...")
                    else:
                        logger.info(f"Request Data: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                else:
                    logger.info(f"Request Data: {str(data)[:500]}")
        except Exception as e:
            logger.warning(f"无法记录请求数据: {e}")

@app.after_request
def log_response(response):
    """记录所有响应"""
    logger.info(f"Response Status: {response.status_code}")
    if response.status_code >= 400:
        logger.error(f"Response Error: {response.get_data(as_text=True)[:500]}")
    logger.info(f"━━━━ 请求结束 ━━━━\n")
    return response

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
MODELS_CONFIG = os.path.join(CONFIG_DIR, 'models.json')
TOOLS_CONFIG = os.path.join(CONFIG_DIR, 'tools.json')
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')

# 确保目录存在
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


def load_json_config(path, default=None):
    """加载 JSON 配置文件"""
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败 {path}: {e}")
    return default or []


def save_json_config(path, data):
    """保存 JSON 配置文件"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存配置失败 {path}: {e}")
        return False


# ==================== 模型管理 ====================

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取所有已注册的模型"""
    models = load_json_config(MODELS_CONFIG, [])
    return jsonify({'success': True, 'models': models})


@app.route('/api/models/test', methods=['POST'])
def test_model():
    """测试模型连接（不保存）"""
    try:
        data = request.json
        url = data.get('url', '').strip()
        api_key = data.get('api_key', '').strip()
        model_type = data.get('model_type', 'openai')
        actual_model_name = data.get('actual_model_name', 'gpt-3.5-turbo')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL 不能为空'})
        
        # 测试连接
        test_result = test_model_connection(url, api_key, model_type, actual_model_name)
        return jsonify(test_result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/models/register', methods=['POST'])
def register_model():
    """注册新模型"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        actual_model_name = data.get('actual_model_name', '').strip()
        url = data.get('url', '').strip()
        api_key = data.get('api_key', '').strip()
        model_type = data.get('model_type', 'openai')  # openai, claude, custom
        
        if not name or not url:
            return jsonify({'success': False, 'error': '模型名称和 URL 不能为空'})
        
        # 加载现有模型
        models = load_json_config(MODELS_CONFIG, [])
        
        # 检查是否已存在
        for model in models:
            if model['name'] == name:
                return jsonify({'success': False, 'error': '模型名称已存在'})
        
        # 添加新模型
        new_model = {
            'id': f"model_{len(models) + 1}_{int(datetime.now().timestamp())}",
            'name': name,
            'actual_model_name': actual_model_name,
            'url': url,
            'api_key': api_key,
            'model_type': model_type,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        models.append(new_model)
        
        # 保存配置
        if save_json_config(MODELS_CONFIG, models):
            return jsonify({'success': True, 'model': new_model})
        else:
            return jsonify({'success': False, 'error': '保存模型配置失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/models/<model_id>', methods=['PUT'])
def update_model(model_id):
    """更新模型（主要是系统提示词）"""
    try:
        data = request.json
        system_prompt = data.get('system_prompt', '')
        
        models = load_json_config(MODELS_CONFIG, [])
        
        for model in models:
            if model['id'] == model_id:
                model['system_prompt'] = system_prompt
                model['updated_at'] = datetime.now().isoformat()
                break
        
        if save_json_config(MODELS_CONFIG, models):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '保存配置失败'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/models/<model_id>', methods=['DELETE'])
def delete_model(model_id):
    """删除模型"""
    try:
        models = load_json_config(MODELS_CONFIG, [])
        models = [m for m in models if m['id'] != model_id]
        
        if save_json_config(MODELS_CONFIG, models):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '保存配置失败'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def test_model_connection(url, api_key, model_type, actual_model_name='gpt-3.5-turbo'):
    """测试模型连接"""
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        
        if api_key:
            if model_type == 'openai':
                headers['Authorization'] = f'Bearer {api_key}'
            elif model_type == 'claude':
                headers['x-api-key'] = api_key
                headers['anthropic-version'] = '2023-06-01'
        
        # 构造测试请求
        if model_type == 'openai':
            test_data = {
                'model': actual_model_name,
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 5
            }
            endpoint = url if url.endswith('/chat/completions') else f"{url.rstrip('/')}/chat/completions"
        elif model_type == 'claude':
            test_data = {
                'model': actual_model_name,
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 5
            }
            endpoint = url if url.endswith('/messages') else f"{url.rstrip('/')}/messages"
        else:
            # 自定义类型，尝试 OpenAI 格式
            test_data = {
                'model': actual_model_name,
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 5
            }
            endpoint = url
        
        response = requests.post(endpoint, json=test_data, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            return {'success': True}
        else:
            return {'success': False, 'error': f"HTTP {response.status_code}: {response.text[:200]}"}
            
    except requests.exceptions.Timeout:
        return {'success': False, 'error': '连接超时'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': '无法连接到服务器'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ==================== 工具管理 ====================

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """获取所有已注册的工具"""
    tools = load_json_config(TOOLS_CONFIG, [])
    return jsonify({'success': True, 'tools': tools})


@app.route('/api/tools/register', methods=['POST'])
def register_tool():
    """注册新工具"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        parameters = data.get('parameters', {})
        
        if not name or not description:
            return jsonify({'success': False, 'error': '工具名称和描述不能为空'})
        
        # 加载现有工具
        tools = load_json_config(TOOLS_CONFIG, [])
        
        # 检查是否已存在
        for tool in tools:
            if tool['name'] == name:
                return jsonify({'success': False, 'error': '工具名称已存在'})
        
        # 添加新工具
        new_tool = {
            'id': f"tool_{len(tools) + 1}_{int(datetime.now().timestamp())}",
            'name': name,
            'description': description,
            'parameters': parameters,
            'created_at': datetime.now().isoformat(),
            'enabled': True
        }
        tools.append(new_tool)
        
        # 保存配置
        if save_json_config(TOOLS_CONFIG, tools):
            return jsonify({'success': True, 'tool': new_tool})
        else:
            return jsonify({'success': False, 'error': '保存工具配置失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/tools/<tool_id>', methods=['DELETE'])
def delete_tool(tool_id):
    """删除工具"""
    try:
        tools = load_json_config(TOOLS_CONFIG, [])
        tools = [t for t in tools if t['id'] != tool_id]
        
        if save_json_config(TOOLS_CONFIG, tools):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '保存配置失败'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/tools/<tool_id>/toggle', methods=['POST'])
def toggle_tool(tool_id):
    """启用/禁用工具"""
    try:
        tools = load_json_config(TOOLS_CONFIG, [])
        
        for tool in tools:
            if tool['id'] == tool_id:
                tool['enabled'] = not tool.get('enabled', True)
                break
        
        if save_json_config(TOOLS_CONFIG, tools):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '保存配置失败'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== 工具执行 ====================

# 导入内置工具（模块化结构）
try:
    from builtin_tools import BUILTIN_TOOLS, BUILTIN_SCHEMAS, list_schemas
    print("✓ 使用模块化 Built-in 工具")
except ImportError as e:
    print(f"✗ 无法加载 builtin_tools 模块: {e}")
    print("✓ 使用内联 Built-in 工具定义（fallback）")
    
    # Fallback: 内联定义（如果模块加载失败）
    BUILTIN_TOOLS = {}
    BUILTIN_SCHEMAS = {}
    
    def register_builtin_tool(name):
        """装饰器：注册内置工具"""
        def decorator(func):
            BUILTIN_TOOLS[name] = func
            return func
        return decorator
    
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
    
    @register_builtin_tool('calculate')
    def tool_calculate(params):
        """计算数学表达式"""
        try:
            expression = params.get('expression', '')
            allowed_chars = set('0123456789+-*/().,e ')
            if not all(c in allowed_chars for c in expression):
                return {'success': False, 'error': '表达式包含非法字符'}
            
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
    
    @register_builtin_tool('search_web')
    def tool_search_web(params):
        """模拟网络搜索"""
        query = params.get('query', '')
        return {
            'success': True,
            'result': {
                'query': query,
                'results': [
                    {'title': f'搜索结果1: {query}', 'snippet': '这是一个示例搜索结果'},
                    {'title': f'搜索结果2: {query}', 'snippet': '这是另一个示例搜索结果'}
                ]
            }
        }
    
    def list_schemas():
        """Fallback: 返回空列表"""
        return []


@app.route('/api/tools/execute', methods=['POST'])
def execute_tool():
    """执行工具调用"""
    try:
        data = request.json
        tool_name = data.get('tool_name')
        parameters = data.get('parameters', {})
        
        if not tool_name:
            return jsonify({'success': False, 'error': '工具名称不能为空'})
        
        # 获取工具配置
        tools = load_json_config(TOOLS_CONFIG, [])
        tool_config = None
        for tool in tools:
            if tool['name'] == tool_name:
                tool_config = tool
                break
        
        if not tool_config:
            return jsonify({'success': False, 'error': f'工具 {tool_name} 未注册'})
        
        # 执行工具
        # 1. 优先使用内置工具
        if tool_name in BUILTIN_TOOLS:
            result = BUILTIN_TOOLS[tool_name](parameters)
            return jsonify(result)
        
        # 2. 如果工具配置了外部API
        if 'api_url' in tool_config:
            try:
                api_url = tool_config['api_url']
                api_method = tool_config.get('api_method', 'POST').upper()
                api_headers = tool_config.get('api_headers', {})
                
                if api_method == 'POST':
                    response = requests.post(api_url, json=parameters, headers=api_headers, timeout=30)
                elif api_method == 'GET':
                    response = requests.get(api_url, params=parameters, headers=api_headers, timeout=30)
                else:
                    return jsonify({'success': False, 'error': f'不支持的HTTP方法: {api_method}'})
                
                if response.status_code in [200, 201]:
                    return jsonify({
                        'success': True,
                        'result': response.json()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'工具API调用失败: HTTP {response.status_code}'
                    })
            except Exception as e:
                return jsonify({'success': False, 'error': f'工具执行错误: {str(e)}'})
        
        # 3. 如果工具配置了Python代码
        if 'code' in tool_config:
            try:
                # 安全执行自定义代码（生产环境需要更严格的沙箱）
                local_vars = {'params': parameters, 'result': None}
                exec(tool_config['code'], {"__builtins__": {}}, local_vars)
                return jsonify({
                    'success': True,
                    'result': local_vars.get('result')
                })
            except Exception as e:
                return jsonify({'success': False, 'error': f'代码执行错误: {str(e)}'})
        
        return jsonify({'success': False, 'error': '工具未配置执行方法（需要配置 api_url 或 code）'})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/tools/builtin', methods=['GET'])
def get_builtin_tools():
    """获取内置工具列表"""
    try:
        # 尝试使用模块化的 schemas
        builtin_tools = list_schemas()
    except:
        # Fallback: 使用内联定义
        builtin_tools = []
        builtin_schemas = {
            'get_current_time': {
                'name': 'get_current_time',
                'description': '获取当前日期和时间',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'timezone': {
                            'type': 'string',
                            'description': '时区，如 UTC, Asia/Shanghai'
                        }
                    }
                }
            },
            'calculate': {
                'name': 'calculate',
                'description': '计算数学表达式',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'expression': {
                            'type': 'string',
                            'description': '要计算的数学表达式'
                        }
                    },
                    'required': ['expression']
                }
            },
            'search_web': {
                'name': 'search_web',
                'description': '搜索网络信息',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': '搜索关键词'
                        }
                    },
                    'required': ['query']
                }
            }
        }
        for name in BUILTIN_TOOLS.keys():
            if name in builtin_schemas:
                builtin_tools.append(builtin_schemas[name])
    
    return jsonify({'success': True, 'tools': builtin_tools})


# ==================== 对话功能 ====================

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理对话请求（非流式）"""
    try:
        data = request.json
        model_id = data.get('model_id')
        messages = data.get('messages', [])
        enabled_tools = data.get('enabled_tools', [])
        params = data.get('params', {})
        
        if not model_id or not messages:
            return jsonify({'success': False, 'error': '缺少必要参数'})
        
        # 获取模型配置
        models = load_json_config(MODELS_CONFIG, [])
        model = None
        for m in models:
            if m['id'] == model_id:
                model = m
                break
        
        if not model:
            return jsonify({'success': False, 'error': '模型不存在'})
        
        # 获取启用的工具
        tools = load_json_config(TOOLS_CONFIG, [])
        active_tools = [t for t in tools if t['id'] in enabled_tools and t.get('enabled', True)]
        
        # 调用模型
        result = call_model(model, messages, active_tools, params)
        
        return jsonify(result)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """处理对话请求（流式）- 传统模式"""
    try:
        data = request.json
        model_id = data.get('model_id')
        messages = data.get('messages', [])
        enabled_tools = data.get('enabled_tools', [])
        params = data.get('params', {})
        
        if not model_id or not messages:
            def error_gen():
                yield f"data: {json.dumps({'type': 'error', 'error': '缺少必要参数'})}\n\n"
            return Response(error_gen(), mimetype='text/event-stream')
        
        # 获取模型配置
        models = load_json_config(MODELS_CONFIG, [])
        model = None
        for m in models:
            if m['id'] == model_id:
                model = m
                break
        
        if not model:
            def error_gen():
                yield f"data: {json.dumps({'type': 'error', 'error': '模型不存在'})}\n\n"
            return Response(error_gen(), mimetype='text/event-stream')
        
        # 获取启用的工具
        tools = load_json_config(TOOLS_CONFIG, [])
        active_tools = [t for t in tools if t['id'] in enabled_tools and t.get('enabled', True)]
        
        # 流式调用模型
        return Response(
            stream_with_context(call_model_stream(model, messages, active_tools, params)),
            mimetype='text/event-stream'
        )
        
    except Exception as e:
        traceback.print_exc()
        def error_gen():
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        return Response(error_gen(), mimetype='text/event-stream')


@app.route('/api/chat/mcp', methods=['POST'])
def chat_mcp():
    """处理对话请求（MCP协调模式）- 支持自动工具调用循环"""
    try:
        data = request.json
        model_id = data.get('model_id')
        messages = data.get('messages', [])
        enabled_tools = data.get('enabled_tools', [])
        params = data.get('params', {})
        auto_parse = data.get('auto_parse', False)
        
        if not model_id or not messages:
            def error_gen():
                yield f"data: {json.dumps({'type': 'error', 'error': '缺少必要参数'})}\n\n"
            return Response(error_gen(), mimetype='text/event-stream')
        
        # 获取模型配置
        models = load_json_config(MODELS_CONFIG, [])
        model = None
        for m in models:
            if m['id'] == model_id:
                model = m
                break
        
        if not model:
            def error_gen():
                yield f"data: {json.dumps({'type': 'error', 'error': '模型不存在'})}\n\n"
            return Response(error_gen(), mimetype='text/event-stream')
        
        # 获取启用的工具
        tools = load_json_config(TOOLS_CONFIG, [])
        active_tools = [t for t in tools if t['id'] in enabled_tools and t.get('enabled', True)]
        
        # 创建模型调用函数（返回字典而非SSE格式）
        def model_caller(msgs, tools_list, model_params):
            """包装模型调用，将SSE格式转换为字典"""
            for sse_chunk in call_model_stream(model, msgs, tools_list, model_params):
                # SSE格式: "data: {...}\n\n"
                if sse_chunk.startswith('data: '):
                    json_str = sse_chunk[6:].strip()
                    if json_str and json_str != '[DONE]':
                        try:
                            yield json.loads(json_str)
                        except json.JSONDecodeError:
                            pass
        
        # 创建工具执行函数
        def tool_executor(tool_name, tool_args):
            return execute_tool_call(tool_name, tool_args)
        
        # 创建MCP协调器
        mcp = MCPCoordinator(model_caller, tool_executor)
        
        # 使用MCP协调器处理请求
        def mcp_generator():
            for event in mcp.coordinate_stream(messages, active_tools, params, auto_parse):
                yield format_mcp_event_for_sse(event)
        
        return Response(
            stream_with_context(mcp_generator()),
            mimetype='text/event-stream'
        )
        
    except Exception as e:
        traceback.print_exc()
        def error_gen():
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        return Response(error_gen(), mimetype='text/event-stream')


def execute_tool_call(tool_name, tool_arguments):
    """执行单个工具调用"""
    logger.info(f"🔧 执行工具调用: {tool_name}")
    logger.debug(f"   参数: {json.dumps(tool_arguments, ensure_ascii=False)}")
    
    start_time = time.time()
    try:
        # 获取工具配置
        tools = load_json_config(TOOLS_CONFIG, [])
        tool_config = None
        for tool in tools:
            if tool['name'] == tool_name:
                tool_config = tool
                break
        
        if not tool_config:
            logger.error(f"   ❌ 工具未注册: {tool_name}")
            return {'success': False, 'error': f'工具 {tool_name} 未注册'}
        
        # 执行工具
        # 1. 优先使用内置工具
        if tool_name in BUILTIN_TOOLS:
            logger.info(f"   使用内置工具: {tool_name}")
            result = BUILTIN_TOOLS[tool_name](tool_arguments)
            elapsed = time.time() - start_time
            logger.info(f"   ✅ 执行成功 ({elapsed:.2f}s)")
            logger.debug(f"   结果: {json.dumps(result, ensure_ascii=False)[:500]}")
            return result
        
        # 2. 如果工具配置了外部API
        if 'api_url' in tool_config:
            api_url = tool_config['api_url']
            api_method = tool_config.get('api_method', 'POST').upper()
            api_headers = tool_config.get('api_headers', {})
            
            logger.info(f"   调用外部API: {api_method} {api_url}")
            
            if api_method == 'POST':
                response = requests.post(api_url, json=tool_arguments, headers=api_headers, timeout=30)
            elif api_method == 'GET':
                response = requests.get(api_url, params=tool_arguments, headers=api_headers, timeout=30)
            else:
                logger.error(f"   ❌ 不支持的HTTP方法: {api_method}")
                return {'success': False, 'error': f'不支持的HTTP方法: {api_method}'}
            
            elapsed = time.time() - start_time
            if response.status_code in [200, 201]:
                result = {'success': True, 'result': response.json()}
                logger.info(f"   ✅ API调用成功 ({elapsed:.2f}s)")
                logger.debug(f"   响应: {response.text[:500]}")
                return result
            else:
                logger.error(f"   ❌ API调用失败: HTTP {response.status_code} ({elapsed:.2f}s)")
                logger.debug(f"   响应: {response.text[:500]}")
                return {'success': False, 'error': f'工具API调用失败: HTTP {response.status_code}'}
        
        # 3. 如果工具配置了Python代码
        if 'code' in tool_config:
            logger.info(f"   执行自定义代码")
            local_vars = {'params': tool_arguments, 'result': None}
            exec(tool_config['code'], {"__builtins__": {}}, local_vars)
            elapsed = time.time() - start_time
            result = {'success': True, 'result': local_vars.get('result')}
            logger.info(f"   ✅ 代码执行成功 ({elapsed:.2f}s)")
            logger.debug(f"   结果: {json.dumps(result, ensure_ascii=False)[:500]}")
            return result
        
        logger.error(f"   ❌ 工具未配置执行方法")
        return {'success': False, 'error': '工具未配置执行方法'}
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"   ❌ 工具执行异常 ({elapsed:.2f}s): {e}")
        logger.error(traceback.format_exc())
        return {'success': False, 'error': str(e)}


def call_model_stream(model, messages, tools, params):
    """流式调用模型 API，支持工具调用"""
    logger.info(f"🤖 调用模型: {model.get('name', 'Unknown')}")
    logger.debug(f"   模型类型: {model.get('model_type')}")
    logger.debug(f"   URL: {model.get('url')}")
    logger.debug(f"   消息数量: {len(messages)}")
    logger.debug(f"   工具数量: {len(tools) if tools else 0}")
    logger.debug(f"   参数: {params}")
    
    try:
        # 发送初始thinking状态
        yield f"data: {json.dumps({'type': 'status', 'status': 'thinking'})}\n\n"
        
        # 工具调用循环：最多允许5轮工具调用
        max_iterations = 5
        current_messages = messages.copy()
        
        for iteration in range(max_iterations):
            tool_calls_data = []
            accumulated_content = ''
            has_tool_calls = False
            
            headers = {
                'Content-Type': 'application/json',
            }
        
        # 设置认证
        if model.get('api_key'):
            if model['model_type'] == 'openai':
                headers['Authorization'] = f"Bearer {model['api_key']}"
            elif model['model_type'] == 'claude':
                headers['x-api-key'] = model['api_key']
                headers['anthropic-version'] = '2023-06-01'
        
        # 处理消息，如果有系统提示词，添加到开头
        processed_messages = []
        
        # 添加系统提示词（如果有）
        if model.get('system_prompt'):
            processed_messages.append({
                'role': 'system',
                'content': model['system_prompt']
            })
        
        # 处理用户消息
        for msg in messages:
            processed_msg = msg.copy()
            if isinstance(msg.get('content'), list):
                # 已经是多模态格式，直接使用
                processed_messages.append(processed_msg)
            else:
                # 纯文本消息
                processed_messages.append(processed_msg)
        
        # 构造请求数据
        request_data = {
            'messages': processed_messages,
            'temperature': params.get('temperature', 0.7),
            'max_tokens': params.get('max_tokens', 2000),
            'top_p': params.get('top_p', 1.0),
            'stream': True  # 启用流式
        }
        
        # 添加可选参数
        if 'presence_penalty' in params:
            request_data['presence_penalty'] = params['presence_penalty']
        if 'frequency_penalty' in params:
            request_data['frequency_penalty'] = params['frequency_penalty']
        
        # 添加模型名称
        actual_model = model.get('actual_model_name', '')
        if model['model_type'] == 'openai':
            request_data['model'] = actual_model or 'gpt-3.5-turbo'
        elif model['model_type'] == 'claude':
            request_data['model'] = actual_model or 'claude-3-sonnet-20240229'
        else:
            request_data['model'] = actual_model or 'default'
        
        # 添加工具定义
        if tools:
            if model['model_type'] in ['openai', 'custom']:
                request_data['tools'] = [
                    {
                        'type': 'function',
                        'function': {
                            'name': tool['name'],
                            'description': tool['description'],
                            'parameters': tool.get('parameters', {})
                        }
                    }
                    for tool in tools
                ]
            elif model['model_type'] == 'claude':
                request_data['tools'] = [
                    {
                        'name': tool['name'],
                        'description': tool['description'],
                        'input_schema': tool.get('parameters', {})
                    }
                    for tool in tools
                ]
        
        # 确定端点
        url = model['url']
        if model['model_type'] == 'openai':
            if not url.endswith('/chat/completions'):
                url = f"{url.rstrip('/')}/chat/completions"
        elif model['model_type'] == 'claude':
            if not url.endswith('/messages'):
                url = f"{url.rstrip('/')}/messages"
        
        # 记录请求数据（隐藏敏感信息）
        request_data_log = request_data.copy()
        # 只记录消息摘要，避免日志过大
        if 'messages' in request_data_log:
            messages_summary = []
            for msg in request_data_log['messages']:
                msg_summary = {'role': msg.get('role')}
                content = msg.get('content', '')
                if isinstance(content, str):
                    msg_summary['content'] = content[:100] + ('...' if len(content) > 100 else '')
                else:
                    msg_summary['content'] = '[multimodal]'
                messages_summary.append(msg_summary)
            request_data_log['messages'] = messages_summary
        
        logger.debug(f"   请求数据: {json.dumps(request_data_log, ensure_ascii=False, indent=2)}")
        
        # 发送流式请求
        logger.debug(f"   发送请求到: {url}")
        response = requests.post(url, json=request_data, headers=headers, stream=True, timeout=60)
        logger.debug(f"   响应状态: {response.status_code}")
        
        if response.status_code in [200, 201]:
            first_content = True
            accumulated_response = ''  # 累积响应内容用于日志
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if model['model_type'] in ['openai', 'custom']:
                                delta = data.get('choices', [{}])[0].get('delta', {})
                                content = delta.get('content', '')
                                
                                # 检查是否有工具调用
                                tool_calls = delta.get('tool_calls')
                                if tool_calls:
                                    yield f"data: {json.dumps({'type': 'status', 'status': 'function_calling'})}\n\n"
                                
                                if content:
                                    # 累积响应内容
                                    accumulated_response += content
                                    
                                    # 第一次收到内容时，切换到answering状态
                                    if first_content:
                                        yield f"data: {json.dumps({'type': 'status', 'status': 'answering'})}\n\n"
                                        first_content = False
                                    
                                    # 直接发送内容，前端会解析 <think> 标签
                                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                                    
                            elif model['model_type'] == 'claude':
                                if data.get('type') == 'content_block_delta':
                                    content = data.get('delta', {}).get('text', '')
                                    if content:
                                        # 累积响应内容
                                        accumulated_response += content
                                        
                                        if first_content:
                                            yield f"data: {json.dumps({'type': 'status', 'status': 'answering'})}\n\n"
                                            first_content = False
                                        yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                        except json.JSONDecodeError:
                            pass
            
            # 记录完整的模型响应
            if accumulated_response:
                response_preview = accumulated_response[:500] + ('...' if len(accumulated_response) > 500 else '')
                logger.info(f"   ✅ 模型响应完成 (长度: {len(accumulated_response)} 字符)")
                logger.debug(f"   响应内容: {response_preview}")
            else:
                logger.warning(f"   ⚠️ 模型响应为空")
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        else:
            logger.error(f"   ❌ API调用失败: HTTP {response.status_code}")
            error_msg = f'API 调用失败: HTTP {response.status_code}'
            try:
                error_detail = response.json()
                if 'error' in error_detail:
                    error_msg += f" - {error_detail['error'].get('message', '')}"
                    logger.error(f"   错误详情: {error_detail}")
            except:
                error_text = response.text[:200]
                error_msg += f" - {error_text}"
                logger.error(f"   错误响应: {error_text}")
            
            yield f"data: {json.dumps({'type': 'status', 'status': 'error'})}\n\n"
            yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
    except requests.exceptions.Timeout:
        logger.error(f"   ❌ 请求超时")
        yield f"data: {json.dumps({'type': 'status', 'status': 'error'})}\n\n"
        yield f"data: {json.dumps({'type': 'error', 'error': '请求超时，请稍后重试'})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    except requests.exceptions.ConnectionError as e:
        logger.error(f"   ❌ 连接错误: {e}")
        yield f"data: {json.dumps({'type': 'status', 'status': 'error'})}\n\n"
        yield f"data: {json.dumps({'type': 'error', 'error': '无法连接到模型服务器'})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    except Exception as e:
        logger.error(f"   ❌ 未知错误: {e}")
        logger.error(traceback.format_exc())
        yield f"data: {json.dumps({'type': 'status', 'status': 'error'})}\n\n"
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"


def call_model(model, messages, tools, params):
    """调用模型 API"""
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        
        # 设置认证
        if model.get('api_key'):
            if model['model_type'] == 'openai':
                headers['Authorization'] = f"Bearer {model['api_key']}"
            elif model['model_type'] == 'claude':
                headers['x-api-key'] = model['api_key']
                headers['anthropic-version'] = '2023-06-01'
        
        # 处理消息，如果有系统提示词，添加到开头
        processed_messages = []
        
        # 添加系统提示词（如果有）
        if model.get('system_prompt'):
            processed_messages.append({
                'role': 'system',
                'content': model['system_prompt']
            })
        
        # 添加用户消息
        processed_messages.extend(messages)
        
        # 构造请求数据
        request_data = {
            'messages': processed_messages,
            'temperature': params.get('temperature', 0.7),
            'max_tokens': params.get('max_tokens', 2000),
            'top_p': params.get('top_p', 1.0),
        }
        
        # 添加可选参数
        if 'presence_penalty' in params:
            request_data['presence_penalty'] = params['presence_penalty']
        if 'frequency_penalty' in params:
            request_data['frequency_penalty'] = params['frequency_penalty']
        
        # 添加模型名称（使用注册时设置的实际模型名）
        actual_model = model.get('actual_model_name', '')
        if model['model_type'] == 'openai':
            request_data['model'] = actual_model or 'gpt-3.5-turbo'
        elif model['model_type'] == 'claude':
            request_data['model'] = actual_model or 'claude-3-sonnet-20240229'
        else:
            request_data['model'] = actual_model or 'default'
        
        # 添加工具定义
        if tools:
            if model['model_type'] in ['openai', 'custom']:
                request_data['tools'] = [
                    {
                        'type': 'function',
                        'function': {
                            'name': tool['name'],
                            'description': tool['description'],
                            'parameters': tool.get('parameters', {})
                        }
                    }
                    for tool in tools
                ]
            elif model['model_type'] == 'claude':
                request_data['tools'] = [
                    {
                        'name': tool['name'],
                        'description': tool['description'],
                        'input_schema': tool.get('parameters', {})
                    }
                    for tool in tools
                ]
        
        # 确定端点
        url = model['url']
        if model['model_type'] == 'openai':
            if not url.endswith('/chat/completions'):
                url = f"{url.rstrip('/')}/chat/completions"
        elif model['model_type'] == 'claude':
            if not url.endswith('/messages'):
                url = f"{url.rstrip('/')}/messages"
        
        # 发送请求
        response = requests.post(url, json=request_data, headers=headers, timeout=60)
        
        if response.status_code in [200, 201]:
            result = response.json()
            
            # 提取回复内容
            if model['model_type'] == 'openai' or model['model_type'] == 'custom':
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                tool_calls = result.get('choices', [{}])[0].get('message', {}).get('tool_calls', [])
            elif model['model_type'] == 'claude':
                content_blocks = result.get('content', [])
                content = ''
                tool_calls = []
                for block in content_blocks:
                    if block.get('type') == 'text':
                        content += block.get('text', '')
                    elif block.get('type') == 'tool_use':
                        tool_calls.append(block)
            else:
                content = str(result)
                tool_calls = []
            
            return {
                'success': True,
                'content': content,
                'tool_calls': tool_calls,
                'raw_response': result
            }
        else:
            return {
                'success': False,
                'error': f"API 调用失败: HTTP {response.status_code}\n{response.text}"
            }
            
    except requests.exceptions.Timeout:
        return {'success': False, 'error': '请求超时'}
    except Exception as e:
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


# ==================== 图片上传 ====================

@app.route('/api/uploads/clear', methods=['POST'])
def clear_uploads():
    """清空上传文件缓存"""
    try:
        import shutil
        
        # 清空uploads目录
        if os.path.exists(UPLOAD_DIR):
            # 删除目录中的所有文件
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {e}")
            
            return jsonify({
                'success': True,
                'message': '上传缓存已清空'
            })
        else:
            return jsonify({
                'success': True,
                'message': '上传目录不存在，无需清空'
            })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/upload', methods=['POST'])
def upload_media():
    """上传图片或视频"""
    try:
        if 'media' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'})
        
        file = request.files['media']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'})
        
        # 保存文件
        filename = f"{int(datetime.now().timestamp())}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)
        
        # 读取并转换为 base64
        with open(filepath, 'rb') as f:
            media_data = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'filename': filename,
            'base64': media_data,
            'url': f"/uploads/{filename}"
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/uploads/<filename>')
def serve_upload(filename):
    """提供上传的文件"""
    return send_from_directory(UPLOAD_DIR, filename)


# ==================== 静态文件服务 ====================

@app.route('/')
def index():
    """主页"""
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """静态文件"""
    return send_from_directory('static', path)


if __name__ == '__main__':
    print("=" * 60)
    print("行业智能通用运维模型2.0 服务启动中...")
    print("访问地址: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)

