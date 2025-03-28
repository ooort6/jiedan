from app import create_app
from app.models.user import User, db

def create_test_user():
    app = create_app()
    with app.app_context():
        # 检查用户是否已存在
        user = User.query.filter_by(username='admin').first()
        if user:
            print('测试用户已存在')
            return
        
        # 创建新用户
        user = User(username='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        print('创建测试用户成功：', user.to_dict())

if __name__ == '__main__':
    create_test_user() 