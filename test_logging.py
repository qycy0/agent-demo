#!/usr/bin/env python3
"""
测试日志功能
"""

import logging
import sys

# 配置日志（模拟 app.py 的配置）
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_logging_levels():
    """测试不同级别的日志"""
    print("\n" + "="*60)
    print("测试日志级别")
    print("="*60 + "\n")
    
    logger.debug("这是 DEBUG 级别日志 - 详细信息")
    logger.info("这是 INFO 级别日志 - 一般信息")
    logger.warning("这是 WARNING 级别日志 - 警告信息")
    logger.error("这是 ERROR 级别日志 - 错误信息")
    logger.critical("这是 CRITICAL 级别日志 - 严重错误")

def test_request_logging():
    """模拟请求日志"""
    print("\n" + "="*60)
    print("测试请求日志")
    print("="*60 + "\n")
    
    logger.info("━━━━ 新请求 ━━━━")
    logger.info("Method: POST")
    logger.info("Path: /api/chat/mcp")
    logger.info("IP: 127.0.0.1")
    logger.info("Request Data: messages=[3 items], ...")
    logger.info("Response Status: 200")
    logger.info("━━━━ 请求结束 ━━━━")

def test_model_logging():
    """模拟模型调用日志"""
    print("\n" + "="*60)
    print("测试模型调用日志")
    print("="*60 + "\n")
    
    logger.info("🤖 调用模型: GPT-4")
    logger.debug("   模型类型: openai")
    logger.debug("   URL: https://api.openai.com/v1")
    logger.debug("   消息数量: 3")
    logger.debug("   工具数量: 2")
    logger.debug("   参数: {'temperature': 0.7, 'max_tokens': 2000}")
    
    # 模拟请求数据
    import json
    request_data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "现在几点？"}
        ],
        "temperature": 0.7,
        "model": "gpt-4-turbo",
        "stream": True
    }
    logger.debug(f"   请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
    logger.debug("   发送请求到: https://api.openai.com/v1/chat/completions")
    logger.debug("   响应状态: 200")
    
    # 模拟响应
    response_content = '<think>用户询问时间，我需要调用get_current_time工具</think><tool_call>{"name":"get_current_time","arguments":{"timezone":"Asia/Shanghai"}}</tool_call>'
    logger.info(f"   ✅ 模型响应完成 (长度: {len(response_content)} 字符)")
    logger.debug(f"   响应内容: {response_content[:200]}...")

def test_tool_logging():
    """模拟工具执行日志"""
    print("\n" + "="*60)
    print("测试工具执行日志")
    print("="*60 + "\n")
    
    logger.info("🔧 执行工具调用: get_current_time")
    logger.debug('   参数: {"timezone":"Asia/Shanghai"}')
    logger.info("   使用内置工具: get_current_time")
    logger.info("   ✅ 执行成功 (0.02s)")
    logger.debug('   结果: {"success":true,"result":{"datetime":"2024-12-04 12:00:00"}}')

def test_mcp_logging():
    """模拟 MCP 协调日志"""
    print("\n" + "="*60)
    print("测试 MCP 协调日志")
    print("="*60 + "\n")
    
    logger.info("🔄 MCP协调开始")
    logger.debug("   消息数量: 3")
    logger.debug("   工具数量: 2")
    logger.debug("   自动解析: True")
    logger.debug("   最大迭代: 5")
    logger.info("   🔁 第 1 轮迭代开始")
    logger.info("      🔧 执行工具: get_current_time")
    logger.debug('         参数: {"timezone":"Asia/Shanghai"}')
    logger.info("         ✅ 工具执行成功")

def test_error_logging():
    """模拟错误日志"""
    print("\n" + "="*60)
    print("测试错误日志")
    print("="*60 + "\n")
    
    logger.info("🔧 执行工具调用: nonexistent_tool")
    logger.error("   ❌ 工具未注册: nonexistent_tool")
    
    logger.info("🤖 调用模型: TestModel")
    logger.error("   ❌ API调用失败: HTTP 500 (1.23s)")
    logger.debug("   响应: Internal Server Error")
    
    try:
        raise ValueError("这是一个测试异常")
    except Exception as e:
        logger.error(f"   ❌ 工具执行异常 (0.05s): {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("日志功能测试")
    print("="*60)
    
    test_logging_levels()
    test_request_logging()
    test_model_logging()
    test_tool_logging()
    test_mcp_logging()
    test_error_logging()
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)
    print("\n提示: 在实际应用中，这些日志会保存到 app.log 文件")
    print("使用 'tail -f app.log' 可以实时查看日志")
    print("\n更多信息请查看: LOG_GUIDE.md\n")

if __name__ == '__main__':
    main()

