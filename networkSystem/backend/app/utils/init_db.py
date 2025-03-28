from app import create_app
from app.models.music import Song, db

def init_test_data():
    app = create_app()
    with app.app_context():
        # 清空现有数据
        Song.query.delete()
        
        # 添加测试歌曲
        songs = [
            {
                'title': '起风了',
                'artist': '买辣椒也用券',
                'album': '起风了',
                'duration': 312,
                'cover_url': 'https://p2.music.126.net/diGAyEmpymX8G7JcnElncQ==/109951163699673355.jpg',
                'source_url': 'https://music.163.com/song/media/outer/url?id=1330348068.mp3'
            },
            {
                'title': '海阔天空',
                'artist': 'Beyond',
                'album': '海阔天空',
                'duration': 326,
                'cover_url': 'https://p1.music.126.net/8y8KJC1eCSO_vUKf2MyZwA==/109951165796899183.jpg',
                'source_url': 'https://music.163.com/song/media/outer/url?id=347230.mp3'
            },
            {
                'title': '晴天',
                'artist': '周杰伦',
                'album': '叶惠美',
                'duration': 269,
                'cover_url': 'https://p1.music.126.net/yjVbsgfNeF2h7fIvnxuZDQ==/109951163894860600.jpg',
                'source_url': 'https://music.163.com/song/media/outer/url?id=186016.mp3'
            },
            {
                'title': '光年之外',
                'artist': '邓紫棋',
                'album': '光年之外',
                'duration': 235,
                'cover_url': 'https://p2.music.126.net/fkqFqMaEt0CzxYS-0NpCog==/18587244069235039.jpg',
                'source_url': 'https://music.163.com/song/media/outer/url?id=449818741.mp3'
            },
            {
                'title': '平凡之路',
                'artist': '朴树',
                'album': '猎户星座',
                'duration': 293,
                'cover_url': 'https://p2.music.126.net/W_5XiCv3rGS1-J7EXpHSCQ==/18885211718782327.jpg',
                'source_url': 'https://music.163.com/song/media/outer/url?id=28815250.mp3'
            }
        ]
        
        for song_data in songs:
            song = Song(**song_data)
            db.session.add(song)
        
        db.session.commit()
        print("测试数据添加成功！")

if __name__ == '__main__':
    init_test_data() 