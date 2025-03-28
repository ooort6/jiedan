from flask import Blueprint, request, jsonify
from app.models.todo import Todo, db
from app.api.auth import token_required
from sqlalchemy import or_

bp = Blueprint('todo', __name__)

@bp.route('', methods=['GET'])
@token_required
def get_todo_list(current_user):
    """获取待办事项列表"""
    try:
        # 获取分页参数
        page = int(request.args.get('current', 1))
        size = int(request.args.get('size', 10))
        keyword = request.args.get('keyword', '')

        # 构建查询
        query = Todo.query.filter_by(user_id=current_user.id, deleted=False)
        
        # 如果有关键字，添加搜索条件
        if keyword:
            query = query.filter(
                or_(
                    Todo.title.like(f'%{keyword}%'),
                    Todo.description.like(f'%{keyword}%')
                )
            )
        
        # 执行分页查询
        pagination = query.order_by(Todo.create_time.desc()).paginate(
            page=page, per_page=size, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'records': [todo.to_dict() for todo in pagination.items],
                'total': pagination.total,
                'size': size,
                'current': page,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': '获取待办事项列表失败',
            'error': str(e)
        }), 500

@bp.route('', methods=['POST'])
@token_required
def create_todo(current_user):
    """创建待办事项"""
    try:
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({
                'code': 400,
                'message': '标题不能为空'
            }), 400
            
        todo = Todo(
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False),
            user_id=current_user.id
        )
        
        db.session.add(todo)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': todo.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': '创建待办事项失败',
            'error': str(e)
        }), 500

@bp.route('/<int:todo_id>', methods=['PUT'])
@token_required
def update_todo(current_user, todo_id):
    """更新待办事项"""
    try:
        todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
        
        if not todo:
            return jsonify({
                'code': 404,
                'message': '待办事项不存在'
            }), 404
            
        data = request.get_json()
        
        if 'title' in data:
            todo.title = data['title']
        if 'description' in data:
            todo.description = data['description']
        if 'completed' in data:
            todo.completed = data['completed']
        if 'deleted' in data:
            todo.deleted = bool(data['deleted'])
            
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': todo.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': '更新待办事项失败',
            'error': str(e)
        }), 500

@bp.route('/<int:todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    """删除待办事项"""
    try:
        todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()
        
        if not todo:
            return jsonify({
                'code': 404,
                'message': '待办事项不存在'
            }), 404
            
        # 软删除
        todo.deleted = True
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': '删除待办事项失败',
            'error': str(e)
        }), 500 