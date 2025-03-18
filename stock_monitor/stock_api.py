import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_stock_data(code, check_name=None):
    """获取股票数据
    
    Args:
        code (str): 股票代码，如 '000001'
        check_name (str, optional): 要验证的股票名称
        
    Returns:
        dict: 股票数据，包含价格、均线等信息
        None: 获取失败时返回
    """
    try:
        # 转换股票代码格式
        if code.startswith('6'):
            full_code = f"sh{code}"
        else:
            full_code = f"sz{code}"
        
        # 构建请求URL
        url = f'http://qt.gtimg.cn/q={full_code}'
        
        # 发送请求
        response = requests.get(url)
        response.encoding = 'gbk'  # 设置正确的编码
        data = response.text
        
        if 'v_pv_none_match' not in data:
            # 解析返回的数据
            parts = data.split('~')
            if len(parts) > 45:
                # 获取股票名称并验证
                stock_name = parts[1]
                if check_name and stock_name != check_name:
                    logger.error(f"股票代码和名称不匹配: 代码 {code} 的名称为 {stock_name}，输入的名称为 {check_name}")
                    return None
                
                # 提取需要的数据
                current_price = float(parts[3])    # 当前价格
                open_price = float(parts[5])       # 今日开盘价
                prev_close = float(parts[4])       # 昨日收盘价
                prev_prev_close = float(parts[33]) if parts[33] else prev_close  # 前日收盘价
                turnover_rate = float(parts[38])   # 换手率
                volume = float(parts[36])          # 成交量
                amount = float(parts[37])          # 成交额
                
                # 计算5日和10日均价
                ma5 = float(parts[48]) if len(parts) > 48 and parts[48] else current_price
                ma10 = float(parts[49]) if len(parts) > 49 and parts[49] else current_price
                
                # 计算涨跌幅
                today_change = ((current_price - prev_close) / prev_close * 100)  # 今日涨幅
                yesterday_change = ((prev_close - prev_prev_close) / prev_prev_close * 100)  # 昨日涨幅
                
                return {
                    'code': code,
                    'name': stock_name,
                    'current_price': round(current_price, 2),
                    'open_price': round(open_price, 2),
                    'prev_close': round(prev_close, 2),
                    'turnover_rate': round(turnover_rate, 2),
                    'main_force_net': round(amount / 10000, 2),  # 换算为万元
                    'ma5': round(ma5, 2),
                    'ma10': round(ma10, 2),
                    'today_change': round(today_change, 2),      # 今日涨幅
                    'yesterday_change': round(yesterday_change, 2),  # 昨日涨幅
                    'volume': volume,
                    'amount': round(amount / 10000, 2),  # 换算为万元
                    'update_time': datetime.now().strftime('%H:%M:%S')
                }
            else:
                logger.error(f"获取股票 {code} 数据格式错误")
                return None
        else:
            logger.error(f"获取股票 {code} 数据失败: 未找到股票")
            return None
            
    except Exception as e:
        logger.error(f"获取股票 {code} 数据异常: {e}")
        return None

def test_api():
    """测试API是否可用"""
    test_data = get_stock_data('000001')
    return test_data is not None

def verify_stock(code, name):
    """验证股票代码和名称是否匹配
    
    Args:
        code (str): 股票代码
        name (str): 股票名称
        
    Returns:
        bool: 是否匹配
    """
    data = get_stock_data(code, check_name=name)
    return data is not None