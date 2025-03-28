from flask import Flask
from flask_cors import CORS
from app.models.user import db
from app.api.auth import bp as auth_bp

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rt130125@localhost/music_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    CORS(app)
    db.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app 