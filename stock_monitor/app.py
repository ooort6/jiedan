from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# 确保stocks.json文件存在
if not os.path.exists('stocks.json'):
    with open('stocks.json', 'w') as f:
        json.dump({"stocks": []}, f)

def load_stocks():
    with open('stocks.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_stocks(stocks_data):
    with open('stocks.json', 'w', encoding='utf-8') as f:
        json.dump(stocks_data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    stocks = load_stocks()
    return render_template('index.html', stocks=stocks['stocks'])

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    stocks = load_stocks()
    return jsonify(stocks)

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    stocks = load_stocks()
    new_stock = request.json
    
    # 检查股票代码是否已存在
    if not any(stock['code'] == new_stock['code'] for stock in stocks['stocks']):
        stocks['stocks'].append(new_stock)
        save_stocks(stocks)
        return jsonify({"message": "股票添加成功"}), 201
    return jsonify({"message": "股票代码已存在"}), 400

@app.route('/api/stocks/<code>', methods=['DELETE'])
def delete_stock(code):
    stocks = load_stocks()
    stocks['stocks'] = [stock for stock in stocks['stocks'] if stock['code'] != code]
    save_stocks(stocks)
    return jsonify({"message": "股票删除成功"})

if __name__ == '__main__':
    app.run(debug=True) 