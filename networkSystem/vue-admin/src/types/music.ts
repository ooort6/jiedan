// 歌手信息
export interface Artist {
  id: number;
  name: string;
}

// 专辑信息
export interface Album {
  id: number;
  name: string;
  picUrl: string;
}

// 歌曲信息
export interface Song {
  id: number;
  name: string;
  artists: Artist[];
  album: Album;
  duration: number;
}

// 歌单信息
export interface Playlist {
  id: number;
  name: string;
  coverImgUrl: string;
  trackCount: number;
  tracks?: Track[];
}

// 歌单中的歌曲信息
export interface Track {
  id: number;
  name: string;
  ar: Artist[];
  al: Album;
  dt: number;
}

// 音乐URL信息
export interface MusicUrl {
  id: number;
  url: string;
  br: number;
}

// API响应类型
export interface SearchResponse {
  result: {
    songs?: Song[];
    playlists?: Playlist[];
  };
  code: number;
}

export interface PlaylistDetailResponse {
  playlist: Playlist;
  code: number;
}

export interface MusicUrlResponse {
  data: MusicUrl[];
  code: number;
}

export interface RecommendPlaylistsResponse {
  result: Playlist[];
  code: number;
}
