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
  title: string;
  artist: string;
  album: string;
  duration: number;
  cover_url: string;
  source_url: string;
}

// 歌单信息
export interface Playlist {
  id: number;
  name: string;
  description: string;
  cover_url: string;
  created_at: string;
  song_count: number;
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
  songs: Song[];
}

export interface PlaylistResponse {
  playlists: Playlist[];
}

export interface PlaylistDetailResponse {
  id: number;
  name: string;
  description: string;
  cover_url: string;
  created_at: string;
  songs: Song[];
}

export interface MusicUrlResponse {
  data: MusicUrl[];
  code: number;
}

export interface RecommendPlaylistsResponse {
  result: Playlist[];
  code: number;
}
