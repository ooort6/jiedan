from flask import Blueprint, request, jsonify
from app.models.user import User, db
from datetime import datetime, timedelta
import jwt
import os
from functools import wraps

bp = Blueprint('auth', __name__)

# JWT配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({
                'code': 401,
                'message': '缺少token!'
            }), 401
            
        try:
            token = token.split(' ')[1]  # Bearer token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({
                'code': 401,
                'message': '无效的token!'
            }), 401
            
        return f(current_user, *args, **kwargs)
        
    return decorated

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 验证必要字段
    if not all(k in data for k in ('username', 'password')):
        return jsonify({
            'code': 400,
            'message': '缺少必要字段!'
        }), 400
        
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'code': 400,
            'message': '用户名已存在!'
        }), 400
        
    # 创建新用户
    user = User(username=data['username'])
    user.set_password(data['password'])
    
    if 'email' in data:
        user.email = data['email']
        
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'code': 201,
            'message': '注册成功!',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': '注册失败!',
            'error': str(e)
        }), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ('username', 'password')):
        return jsonify({
            'code': 400,
            'message': '缺少必要字段!'
        }), 400
        
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 生成JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.utcnow() + timedelta(days=1)
            },
            SECRET_KEY,
            algorithm="HS256"
        )
        
        return jsonify({
            'code': 200,
            'message': '登录成功!',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    return jsonify({
        'code': 401,
        'message': '用户名或密码错误!'
    }), 401

@bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    # 由于使用的是JWT，服务器端不需要做特殊处理
    # 客户端只需要删除本地存储的token即可
    return jsonify({
        'code': 200,
        'message': '登出成功!'
    }), 200

@bp.route('/info', methods=['GET'])
@token_required
def get_user_info(current_user):
    """获取当前登录用户信息"""
    return jsonify({
        'code': 200,
        'message': '获取用户信息成功',
        'data': current_user.to_dict()
    }), 200 