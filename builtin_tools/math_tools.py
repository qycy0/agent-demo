"""
数学计算工具集
"""

import re

def calculate(params):
    """
    计算数学表达式
    
    Args:
        params (dict):
            - expression (str): 数学表达式
    
    Returns:
        dict: 计算结果
    """
    try:
        expression = params.get('expression', '')
        
        if not expression:
            return {
                'success': False,
                'error': '表达式不能为空'
            }
        
        # 安全检查：只允许数字和基本运算符
        if not re.match(r'^[\d\s\+\-\*/\(\)\.\^%]+$', expression):
            return {
                'success': False,
                'error': '表达式包含非法字符，只允许数字和 + - * / ( ) . ^ % 运算符'
            }
        
        # 替换 ^ 为 **（Python的幂运算）
        expression = expression.replace('^', '**')
        
        # 安全计算
        result = eval(expression, {"__builtins__": {}}, {})
        
        return {
            'success': True,
            'result': {
                'expression': params.get('expression', ''),
                'value': result
            }
        }
        
    except ZeroDivisionError:
        return {
            'success': False,
            'error': '除数不能为零'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'计算错误: {str(e)}'
        }

