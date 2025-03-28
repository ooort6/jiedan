from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.music import Playlist, Song, Favorite, PlaylistSong, db
from datetime import datetime

bp = Blueprint('music', __name__)

# 搜索音乐
@bp.route('/search', methods=['GET'])
def search_music():
    query = request.args.get('query', '')
    print(f"搜索关键词: {query}")  # 添加日志
    if not query:
        return jsonify({'error': '搜索关键词不能为空'}), 400
    
    # 这里实现音乐搜索逻辑，可以调用第三方API或搜索本地数据库
    try:
        songs = Song.query.filter(
            (Song.title.like(f'%{query}%')) |
            (Song.artist.like(f'%{query}%')) |
            (Song.album.like(f'%{query}%'))
        ).all()
        print(f"搜索结果: {songs}")  # 添加日志
        print(f"搜索结果数量: {len(songs)}")  # 添加日志
        
        result = {
            'songs': [{
                'id': song.id,
                'title': song.title,
                'artist': song.artist,
                'album': song.album,
                'duration': song.duration,
                'cover_url': song.cover_url,
                'source_url': song.source_url
            } for song in songs]
        }
        print(f"返回结果: {result}")  # 添加日志
        return jsonify(result)
    except Exception as e:
        print(f"搜索出错: {str(e)}")  # 添加日志
        return jsonify({'error': '搜索失败'}), 500

# 获取用户的播放列表
@bp.route('/playlists', methods=['GET'])
def get_user_playlists():
    playlists = Playlist.query.all()
    
    return jsonify({
        'playlists': [{
            'id': playlist.id,
            'name': playlist.name,
            'description': playlist.description,
            'cover_url': playlist.cover_url,
            'created_at': playlist.created_at.isoformat(),
            'song_count': playlist.songs.count()
        } for playlist in playlists]
    })

# 创建新的播放列表
@bp.route('/playlists', methods=['POST'])
def create_playlist():
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': '播放列表名称不能为空'}), 400
    
    playlist = Playlist(
        name=data['name'],
        description=data.get('description', ''),
        cover_url=data.get('cover_url', ''),
        user_id=1  # 临时使用固定用户ID
    )
    
    db.session.add(playlist)
    db.session.commit()
    
    return jsonify({
        'id': playlist.id,
        'name': playlist.name,
        'description': playlist.description,
        'cover_url': playlist.cover_url,
        'created_at': playlist.created_at.isoformat()
    }), 201

# 获取播放列表详情
@bp.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist_detail(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    
    songs = playlist.songs.all()
    return jsonify({
        'id': playlist.id,
        'name': playlist.name,
        'description': playlist.description,
        'cover_url': playlist.cover_url,
        'created_at': playlist.created_at.isoformat(),
        'songs': [{
            'id': song.id,
            'title': song.title,
            'artist': song.artist,
            'album': song.album,
            'duration': song.duration,
            'cover_url': song.cover_url,
            'source_url': song.source_url
        } for song in songs]
    })

# 添加歌曲到播放列表
@bp.route('/playlists/<int:playlist_id>/songs', methods=['POST'])
def add_song_to_playlist(playlist_id):
    data = request.get_json()
    
    if not data.get('song_id'):
        return jsonify({'error': '歌曲ID不能为空'}), 400
    
    playlist = Playlist.query.get_or_404(playlist_id)
    song = Song.query.get_or_404(data['song_id'])
    
    if song not in playlist.songs:
        playlist_song = PlaylistSong(
            playlist_id=playlist_id,
            song_id=song.id,
            order=playlist.songs.count()
        )
        db.session.add(playlist_song)
        db.session.commit()
    
    return jsonify({'message': '添加成功'})

# 从播放列表中移除歌曲
@bp.route('/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
def remove_song_from_playlist(playlist_id, song_id):
    playlist_song = PlaylistSong.query.filter_by(
        playlist_id=playlist_id,
        song_id=song_id
    ).first_or_404()
    
    db.session.delete(playlist_song)
    db.session.commit()
    
    return jsonify({'message': '删除成功'})

# 获取用户收藏的歌曲
@bp.route('/favorites', methods=['GET'])
def get_favorite_songs():
    favorites = Favorite.query.all()
    
    return jsonify({
        'songs': [{
            'id': fav.song.id,
            'title': fav.song.title,
            'artist': fav.song.artist,
            'album': fav.song.album,
            'duration': fav.song.duration,
            'cover_url': fav.song.cover_url,
            'source_url': fav.song.source_url,
            'favorited_at': fav.created_at.isoformat()
        } for fav in favorites]
    })

# 收藏/取消收藏歌曲
@bp.route('/favorites/<int:song_id>', methods=['POST', 'DELETE'])
def toggle_favorite(song_id):
    favorite = Favorite.query.filter_by(song_id=song_id).first()
    
    if request.method == 'POST':
        if favorite:
            return jsonify({'message': '歌曲已经在收藏列表中'})
        
        song = Song.query.get_or_404(song_id)
        favorite = Favorite(user_id=1, song_id=song_id)  # 临时使用固定用户ID
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'message': '收藏成功'})
    
    else:  # DELETE
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
        return jsonify({'message': '取消收藏成功'})

# 获取推荐歌曲
@bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    # 返回所有歌曲作为推荐
    songs = Song.query.all()
    
    return jsonify({
        'songs': [{
            'id': song.id,
            'title': song.title,
            'artist': song.artist,
            'album': song.album,
            'duration': song.duration,
            'cover_url': song.cover_url,
            'source_url': song.source_url
        } for song in songs]
    })

# 获取推荐歌单
@bp.route('/personalized', methods=['GET'])
def get_personalized():
    playlists = Playlist.query.all()
    return jsonify({
        'result': [{
            'id': playlist.id,
            'name': playlist.name,
            'description': playlist.description,
            'cover_url': playlist.cover_url,
            'created_at': playlist.created_at.isoformat(),
            'song_count': playlist.songs.count()
        } for playlist in playlists]
    }) 