from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime, timedelta
import requests
import time
import threading
import logging

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 存储股票数据的文件
STOCKS_FILE = 'stocks.json'
MA_STOCKS_FILE = 'ma_stocks.json'

# 机器人webhook地址
ROBOT_WEBHOOK_1 = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2d893fc9-2194-40e2-98d0-6bb42599bac2'  # 监控价格机器人
ROBOT_WEBHOOK_2 = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=b58a54a1-a744-43fd-9a78-767ca478053b'  # 监控均线机器人
ROBOT_WEBHOOK_3 = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=742b0a2b-bc4c-4ffd-a080-c943114f3a5b'  # 3号机器人

# Tushare API
try:
    import chinadata.ca_data as ts
    pro = ts.pro_api('ndd07f13a9e334456a6694056e146afed04')
                      
    # 设置API URL
    pro._DataApi__http_url = 'http://tsapi.majors.ltd:7000'
    
    # 测试API是否可用
    test_result = pro.daily(ts_code='000001.SZ')
    if isinstance(test_result, str) and "token无效" in test_result:
        logger.error(f"Tushare API token无效: {test_result}")
        ts = None
        pro = None
    else:
        logger.info("成功初始化Tushare API")
except Exception as e:
    logger.error(f"初始化Tushare API失败: {e}")
    ts = None
    pro = None

# 全局变量，用于控制监控线程
monitoring = False
monitor_thread = None

def load_stocks():
    """从文件加载股票数据"""
    if os.path.exists(STOCKS_FILE):
        with open(STOCKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_stocks(stocks):
    """保存股票数据到文件"""
    with open(STOCKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)

def load_ma_stocks():
    """从文件加载均线监控股票数据"""
    if os.path.exists(MA_STOCKS_FILE):
        with open(MA_STOCKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_ma_stocks(stocks):
    """保存均线监控股票数据到文件"""
    with open(MA_STOCKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)

def is_trading_time():
    """判断当前是否为交易时间"""
    now = datetime.now()
    # 判断是否为工作日
    if now.weekday() >= 5:  # 周六日不交易
        return False
    
    # 判断时间段
    hour, minute = now.hour, now.minute
    time_value = hour * 100 + minute
    
    # 交易时间：9:30-11:30, 13:00-15:00
    return (930 <= time_value <= 1130) or (1300 <= time_value <= 1500)

def get_stock_data(code):
    """获取股票数据"""
    if pro is None:
        logger.warning(f"使用模拟数据代替实际股票 {code} 数据")
        # 返回模拟数据
        return {
            'current_price': 100.0,
            'open_price': 99.0,
            'close_price': 100.0,
            'turnover_rate': 2.5,
            'main_force_net': '暂无数据',
            'ma5': 98.0,
            'ma10': 97.0,
            'today_change': 1.0,
            'yesterday_change': 0.5,
            'amount': 10000.0  # 成交额（万元）
        }
    
    try:
        # 转换股票代码格式
        ts_code = convert_to_tushare_code(code)
        
        # 获取当前日期
        today = datetime.now().strftime('%Y%m%d')
        
        # 获取最近交易日数据
        df_daily = pro.daily(ts_code=ts_code)
        
        # 检查返回的数据类型
        if isinstance(df_daily, str):
            logger.warning(f"获取股票 {code} 数据返回字符串: {df_daily}")
            # 返回模拟数据
            return {
                'current_price': 100.0,
                'open_price': 99.0,
                'close_price': 100.0,
                'turnover_rate': 2.5,
                'main_force_net': '暂无数据',
                'ma5': 98.0,
                'ma10': 97.0,
                'today_change': 1.0,
                'yesterday_change': 0.5,
                'amount': 10000.0  # 成交额（万元）
            }
        
        # 检查DataFrame是否为空
        if hasattr(df_daily, 'empty') and df_daily.empty:
            logger.warning(f"未获取到股票 {code} 的数据")
            return None
        
        # 获取最新一天的数据
        latest_data = df_daily.iloc[0]
        
        # 获取前一天的数据（如果有）
        prev_data = df_daily.iloc[1] if len(df_daily) > 1 else None
        
        # 计算涨跌幅
        today_change = 0
        if prev_data is not None:
            today_change = (latest_data['close'] - prev_data['close']) / prev_data['close'] * 100
        
        # 计算5日和10日均线
        ma5 = df_daily['close'].iloc[:5].mean() if len(df_daily) >= 5 else 0
        ma10 = df_daily['close'].iloc[:10].mean() if len(df_daily) >= 10 else 0
        
        # 获取主力净量数据
        try:
            df_moneyflow = pro.moneyflow(ts_code=ts_code)
            if isinstance(df_moneyflow, str):
                logger.warning(f"获取主力净量数据返回字符串: {df_moneyflow}")
                main_force_net = '暂无数据'
            elif hasattr(df_moneyflow, 'empty') and not df_moneyflow.empty:
                main_force_net = df_moneyflow['net_mf_amount'].iloc[0]
            else:
                main_force_net = '暂无数据'
        except Exception as e:
            logger.error(f"获取主力净量数据失败: {e}")
            main_force_net = '暂无数据'
        
        # 获取实时价格（如果在交易时间内）
        current_price = latest_data['close']
        if is_trading_time():
            try:
                # 获取实时行情
                df_realtime = ts.get_realtime_quotes(ts_code.split('.')[0])
                if isinstance(df_realtime, str):
                    logger.warning(f"获取实时价格返回字符串: {df_realtime}")
                elif hasattr(df_realtime, 'empty') and not df_realtime.empty:
                    current_price = float(df_realtime['price'].iloc[0])
            except Exception as e:
                logger.error(f"获取实时价格失败: {e}")
        
        return {
            'current_price': float(current_price),
            'open_price': float(latest_data['open']),
            'close_price': float(latest_data['close']),
            'turnover_rate': float(latest_data.get('turnover', 0)),
            'main_force_net': main_force_net,
            'ma5': round(float(ma5), 2),
            'ma10': round(float(ma10), 2),
            'today_change': round(float(today_change), 2),
            'yesterday_change': round(float(latest_data.get('pct_chg', 0)), 2),
            'amount': float(latest_data['amount']) / 1000  # 成交额（万元）
        }
    except Exception as e:
        logger.error(f"获取股票 {code} 数据失败: {e}")
        return None

def convert_to_tushare_code(code):
    """转换股票代码为Tushare格式"""
    # 如果已经是Tushare格式，直接返回
    if '.' in code:
        return code
    
    # 尝试根据股票代码前缀判断市场
    if code.startswith('6'):
        return f"{code}.SH"  # 上海市场
    elif code.startswith(('0', '3')):
        return f"{code}.SZ"  # 深圳市场
    elif code.startswith('8'):
        return f"{code}.BJ"  # 北京市场
    else:
        # 默认返回上海市场
        return f"{code}.SH"

def send_wecom_message(webhook_url, content):
    """发送企业微信消息"""
    try:
        payload = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        response = requests.post(webhook_url, json=payload)
        result = response.json()
        
        if result.get('errcode') == 0:
            logger.info(f"消息发送成功: {content[:50]}...")
            return True
        else:
            logger.error(f"消息发送失败: {result}")
            return False
    except Exception as e:
        logger.error(f"发送消息异常: {e}")
        return False

def monitor_stocks():
    """监控股票价格和均线"""
    global monitoring
    
    # 发送系统启动通知
    startup_message = "📢 股票监控系统已启动\n"
    startup_message += f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # 获取监控的股票列表
    price_stocks = load_stocks()
    ma_stocks = load_ma_stocks()
    
    if price_stocks:
        startup_message += "\n🔍 价格监控股票列表:\n"
        for stock in price_stocks:
            note = f"（{stock['note']}）" if stock.get('note') else ""
            startup_message += f"- {stock['name']}{note} 监控价格: {stock['monitor_price']}\n"
    
    if ma_stocks:
        startup_message += "\n📊 均线监控股票列表:\n"
        for stock in ma_stocks:
            note = f"（{stock['note']}）" if stock.get('note') else ""
            startup_message += f"- {stock['name']}{note}\n"
    
    # 只发送到第一个群，避免频率限制
    send_wecom_message(ROBOT_WEBHOOK_1, startup_message)
    
    # 记录已经发送过预警的股票，避免重复发送
    price_alerted = set()
    ma5_alerted = set()
    ma10_alerted = set()
    
    # 记录最后一次发送消息的时间
    last_message_time = datetime.now() - timedelta(minutes=5)
    
    # 监控循环
    while monitoring:
        try:
            # 重新加载股票列表，以获取最新的监控配置
            price_stocks = load_stocks()
            ma_stocks = load_ma_stocks()
            
            # 只在交易时间内进行监控
            if is_trading_time():
                logger.info("当前为交易时间，开始检查股票数据...")
                
                # 监控价格
                for stock in price_stocks:
                    try:
                        data = get_stock_data(stock['code'])
                        if data:
                            # 检查价格是否低于监控价格
                            if data['current_price'] < stock['monitor_price']:
                                alert_key = f"{stock['code']}_{stock['monitor_price']}"
                                if alert_key not in price_alerted:
                                    # 检查消息发送频率
                                    current_time = datetime.now()
                                    if (current_time - last_message_time).total_seconds() < 60:
                                        logger.info("消息发送过于频繁，跳过本次发送")
                                        continue
                                        
                                    note = f"（{stock['note']}）" if stock.get('note') else ""
                                    message = f"⚠️ 价格预警\n股票: {stock['name']}{note}\n当前价格: {data['current_price']}\n监控价格: {stock['monitor_price']}\n时间: {datetime.now().strftime('%H:%M:%S')}"
                                    if send_wecom_message(ROBOT_WEBHOOK_1, message):
                                        price_alerted.add(alert_key)
                                        last_message_time = current_time
                    except Exception as e:
                        logger.error(f"监控股票 {stock['name']} 价格异常: {e}")
                
                # 监控均线
                for stock in ma_stocks:
                    try:
                        data = get_stock_data(stock['code'])
                        if data:
                            # 检查价格是否低于5日均线
                            if data['current_price'] < data['ma5']:
                                alert_key = f"{stock['code']}_ma5_{datetime.now().strftime('%Y%m%d')}"
                                if alert_key not in ma5_alerted:
                                    # 检查消息发送频率
                                    current_time = datetime.now()
                                    if (current_time - last_message_time).total_seconds() < 60:
                                        logger.info("消息发送过于频繁，跳过本次发送")
                                        continue
                                        
                                    note = f"（{stock['note']}）" if stock.get('note') else ""
                                    message = f"📉 均线预警\n股票: {stock['name']}{note}\n当前价格: {data['current_price']}\n5日均线: {data['ma5']}\n低于5日均线: {round(data['ma5'] - data['current_price'], 2)}\n时间: {datetime.now().strftime('%H:%M:%S')}"
                                    if send_wecom_message(ROBOT_WEBHOOK_2, message):
                                        ma5_alerted.add(alert_key)
                                        last_message_time = current_time
                            
                            # 检查价格是否低于10日均线
                            if data['current_price'] < data['ma10']:
                                alert_key = f"{stock['code']}_ma10_{datetime.now().strftime('%Y%m%d')}"
                                if alert_key not in ma10_alerted:
                                    # 检查消息发送频率
                                    current_time = datetime.now()
                                    if (current_time - last_message_time).total_seconds() < 60:
                                        logger.info("消息发送过于频繁，跳过本次发送")
                                        continue
                                        
                                    note = f"（{stock['note']}）" if stock.get('note') else ""
                                    message = f"📉 均线预警\n股票: {stock['name']}{note}\n当前价格: {data['current_price']}\n10日均线: {data['ma10']}\n低于10日均线: {round(data['ma10'] - data['current_price'], 2)}\n时间: {datetime.now().strftime('%H:%M:%S')}"
                                    if send_wecom_message(ROBOT_WEBHOOK_2, message):
                                        ma10_alerted.add(alert_key)
                                        last_message_time = current_time
                    except Exception as e:
                        logger.error(f"监控股票 {stock['name']} 均线异常: {e}")
            else:
                logger.info("当前非交易时间，跳过检查...")
            
            # 每30秒检查一次
            time.sleep(30)
        except Exception as e:
            logger.error(f"监控线程异常: {e}")
            time.sleep(30)  # 发生异常时，等待30秒后继续

def start_monitoring():
    """启动监控线程"""
    global monitoring, monitor_thread
    
    if monitoring:
        return False
    
    monitoring = True
    monitor_thread = threading.Thread(target=monitor_stocks)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    logger.info("监控线程已启动")
    return True

def stop_monitoring():
    """停止监控线程"""
    global monitoring
    
    if not monitoring:
        return False
    
    monitoring = False
    
    # 发送系统关闭通知
    shutdown_message = f"📢 股票监控系统已关闭\n⏰ 关闭时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    send_wecom_message(ROBOT_WEBHOOK_1, shutdown_message)
    send_wecom_message(ROBOT_WEBHOOK_2, shutdown_message)
    
    logger.info("监控线程已停止")
    return True

@app.route('/')
def index():
    """渲染主页"""
    stocks = load_stocks()
    ma_stocks = load_ma_stocks()
    return render_template('index.html', stocks=stocks, ma_stocks=ma_stocks)

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """获取所有股票"""
    stocks = load_stocks()
    return jsonify(stocks)

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    """添加股票"""
    data = request.json
    stocks = load_stocks()
    
    # 检查是否已存在
    if any(s['code'] == data['code'] for s in stocks):
        return jsonify({'success': False, 'message': '股票已存在'})
    
    # 添加新股票
    new_stock = {
        'code': data['code'],
        'name': data['name'],
        'monitor_price': float(data['monitor_price']),
        'note': data.get('note', '')
    }
    
    stocks.append(new_stock)
    save_stocks(stocks)
    
    # 简化消息内容，减少API调用
    try:
        note = f"（{new_stock['note']}）" if new_stock.get('note') else ""
        message = f"➕ 添加价格监控股票\n股票: {new_stock['name']}{note}\n监控价格: {new_stock['monitor_price']}"
        send_wecom_message(ROBOT_WEBHOOK_1, message)
    except Exception as e:
        logger.error(f"发送添加股票通知失败: {e}")
    
    return jsonify({'success': True, 'message': '添加成功'})

@app.route('/api/stocks/<code>', methods=['DELETE'])
def delete_stock(code):
    """删除股票"""
    stocks = load_stocks()
    
    # 查找要删除的股票
    deleted_stock = None
    for stock in stocks:
        if stock['code'] == code:
            deleted_stock = stock
            break
    
    # 删除股票
    stocks = [s for s in stocks if s['code'] != code]
    save_stocks(stocks)
    
    # 简化消息内容，减少API调用
    if deleted_stock:
        try:
            note = f"（{deleted_stock['note']}）" if deleted_stock.get('note') else ""
            message = f"➖ 删除价格监控股票\n股票: {deleted_stock['name']}{note}"
            send_wecom_message(ROBOT_WEBHOOK_1, message)
        except Exception as e:
            logger.error(f"发送删除股票通知失败: {e}")
    
    return jsonify({'success': True, 'message': '删除成功'})

@app.route('/api/stocks/<code>/monitor-price', methods=['PUT'])
def update_monitor_price(code):
    """更新监控价格"""
    data = request.json
    stocks = load_stocks()
    
    # 查找并更新股票
    updated_stock = None
    for stock in stocks:
        if stock['code'] == code:
            old_price = stock['monitor_price']
            stock['monitor_price'] = float(data['monitor_price'])
            updated_stock = stock
            break
    
    save_stocks(stocks)
    
    # 发送通知
    if updated_stock:
        note = f"（{updated_stock['note']}）" if updated_stock.get('note') else ""
        message = f"🔄 更新价格监控\n股票: {updated_stock['name']}{note}\n旧监控价格: {old_price}\n新监控价格: {updated_stock['monitor_price']}"
        send_wecom_message(ROBOT_WEBHOOK_1, message)
    
    return jsonify({'success': True, 'message': '更新成功'})

@app.route('/api/stocks/data')
def get_all_stocks_data():
    """获取所有股票的实时数据"""
    stocks = load_stocks()
    result = []
    
    for stock in stocks:
        data = get_stock_data(stock['code'])
        if data:
            data.update({
                'code': stock['code'],
                'name': stock['name'],
                'monitor_price': stock['monitor_price'],
                'note': stock.get('note', '')
            })
            result.append(data)
    
    return jsonify(result)

@app.route('/api/ma_stocks', methods=['GET'])
def get_ma_stocks():
    """获取所有均线监控股票"""
    stocks = load_ma_stocks()
    return jsonify(stocks)

@app.route('/api/ma_stocks', methods=['POST'])
def add_ma_stock():
    """添加均线监控股票"""
    data = request.json
    stocks = load_ma_stocks()
    
    # 检查是否已存在
    if any(s['code'] == data['code'] for s in stocks):
        return jsonify({'success': False, 'message': '股票已存在'})
    
    # 添加新股票
    new_stock = {
        'code': data['code'],
        'name': data['name'],
        'note': data.get('note', '')
    }
    
    stocks.append(new_stock)
    save_ma_stocks(stocks)
    
    # 简化消息内容，减少API调用
    try:
        note = f"（{new_stock['note']}）" if new_stock.get('note') else ""
        message = f"➕ 添加均线监控股票\n股票: {new_stock['name']}{note}"
        send_wecom_message(ROBOT_WEBHOOK_2, message)
    except Exception as e:
        logger.error(f"发送添加均线监控股票通知失败: {e}")
    
    return jsonify({'success': True, 'message': '添加成功'})

@app.route('/api/ma_stocks/<code>', methods=['DELETE'])
def delete_ma_stock(code):
    """删除均线监控股票"""
    stocks = load_ma_stocks()
    
    # 查找要删除的股票
    deleted_stock = None
    for stock in stocks:
        if stock['code'] == code:
            deleted_stock = stock
            break
    
    # 删除股票
    stocks = [s for s in stocks if s['code'] != code]
    save_ma_stocks(stocks)
    
    # 简化消息内容，减少API调用
    if deleted_stock:
        try:
            note = f"（{deleted_stock['note']}）" if deleted_stock.get('note') else ""
            message = f"➖ 删除均线监控股票\n股票: {deleted_stock['name']}{note}"
            send_wecom_message(ROBOT_WEBHOOK_2, message)
        except Exception as e:
            logger.error(f"发送删除均线监控股票通知失败: {e}")
    
    return jsonify({'success': True, 'message': '删除成功'})

@app.route('/api/ma_stocks/data')
def get_all_ma_stocks_data():
    """获取所有均线监控股票的实时数据"""
    stocks = load_ma_stocks()
    result = []
    
    for stock in stocks:
        data = get_stock_data(stock['code'])
        if data:
            data.update({
                'code': stock['code'],
                'name': stock['name'],
                'note': stock.get('note', '')
            })
            result.append(data)
    
    return jsonify(result)

@app.route('/api/monitor/start', methods=['POST'])
def start_monitor():
    """启动监控"""
    if start_monitoring():
        return jsonify({'success': True, 'message': '监控已启动'})
    else:
        return jsonify({'success': False, 'message': '监控已在运行中'})

@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitor():
    """停止监控"""
    if stop_monitoring():
        return jsonify({'success': True, 'message': '监控已停止'})
    else:
        return jsonify({'success': False, 'message': '监控未在运行'})

@app.route('/api/monitor/status', methods=['GET'])
def monitor_status():
    """获取监控状态"""
    return jsonify({'monitoring': monitoring})

@app.route('/api/alert', methods=['POST'])
def send_alert():
    """发送预警信息"""
    data = request.json
    
    # 构造预警消息
    note = f"（{data.get('note', '')}）" if data.get('note') else ""
    message = f"⚠️ 手动预警\n股票: {data['name']}{note}\n当前价格: {data['price']}\n监控价格: {data['monitor_price']}"
    
    # 发送到机器人
    if send_wecom_message(ROBOT_WEBHOOK_1, message):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '发送预警失败'})

if __name__ == '__main__':
    # 启动监控线程
    start_monitoring()
    
    try:
        # 使用兼容的参数
        app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
    finally:
        # 确保在应用关闭时停止监控线程
        stop_monitoring() 