"""
时间日期工具集
"""

from datetime import datetime
import pytz

def get_current_time(params):
    """
    获取当前时间
    
    Args:
        params (dict):
            - timezone (str): 时区，默认 'UTC'
            - format (str): 格式，'12h' 或 '24h'，默认 '24h'
    
    Returns:
        dict: 包含当前时间信息
    """
    try:
        timezone = params.get('timezone', 'UTC')
        time_format = params.get('format', '24h')
        
        # 获取时区
        try:
            tz = pytz.timezone(timezone)
        except:
            tz = pytz.UTC
        
        now = datetime.now(tz)
        
        # 格式化时间
        if time_format == '12h':
            time_str = now.strftime('%Y-%m-%d %I:%M:%S %p')
        else:
            time_str = now.strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'success': True,
            'result': {
                'datetime': time_str,
                'timezone': str(tz),
                'timestamp': now.timestamp(),
                'iso': now.isoformat()
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'获取时间失败: {str(e)}'
        }

