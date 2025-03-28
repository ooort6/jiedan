from flask import Flask
from flask_cors import CORS
from app.models.user import db
from app.api.auth import bp as auth_bp
from app.api.todo import bp as todo_bp
from app.api.music import bp as music_bp
from flask_jwt_extended import JWTManager
import pymysql

# 让 PyMySQL 模拟 MySQLdb
pymysql.install_as_MySQLdb()

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rt130125@localhost/music_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'  # JWT密钥
    
    # 初始化扩展
    CORS(app, supports_credentials=True)  # 允许跨域请求
    db.init_app(app)
    jwt = JWTManager(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(todo_bp, url_prefix='/api/todos')
    app.register_blueprint(music_bp, url_prefix='/api/music')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app 