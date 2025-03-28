import request from "@/utils/request";
import type {
  SearchResponse,
  PlaylistDetailResponse,
  MusicUrlResponse,
  RecommendPlaylistsResponse,
  PlaylistResponse,
} from "@/types/music";

export interface Song {
  id: number;
  title: string;
  artist: string;
  album: string;
  duration: number;
  cover_url: string;
  source_url: string;
}

export interface Playlist {
  id: number;
  name: string;
  description: string;
  cover_url: string;
  created_at: string;
  song_count: number;
}

// 搜索音乐
export const searchMusic = (keywords: string): Promise<SearchResponse> => {
  return request({
    url: "/music/search",
    method: "get",
    params: { query: keywords },
  });
};

// 获取用户播放列表
export const getUserPlaylists = (): Promise<PlaylistResponse> => {
  return request({
    url: "/music/playlists",
    method: "get",
  });
};

// 创建播放列表
export const createPlaylist = (data: {
  name: string;
  description?: string;
  cover_url?: string;
}) => {
  return request({
    url: "/music/playlists",
    method: "post",
    data,
  });
};

// 获取播放列表详情
export const getPlaylistDetail = (
  playlistId: number
): Promise<PlaylistDetailResponse> => {
  return request({
    url: `/music/playlists/${playlistId}`,
    method: "get",
  });
};

// 添加歌曲到播放列表
export const addSongToPlaylist = (playlistId: number, songId: number) => {
  return request({
    url: `/music/playlists/${playlistId}/songs`,
    method: "post",
    data: { song_id: songId },
  });
};

// 从播放列表移除歌曲
export const removeSongFromPlaylist = (playlistId: number, songId: number) => {
  return request({
    url: `/music/playlists/${playlistId}/songs/${songId}`,
    method: "delete",
  });
};

// 获取收藏的歌曲
export const getFavoriteSongs = () => {
  return request({
    url: "/music/favorites",
    method: "get",
  });
};

// 收藏歌曲
export const addToFavorites = (songId: number) => {
  return request({
    url: `/music/favorites/${songId}`,
    method: "post",
  });
};

// 取消收藏
export const removeFromFavorites = (songId: number) => {
  return request({
    url: `/music/favorites/${songId}`,
    method: "delete",
  });
};

// 获取推荐歌曲
export const getRecommendations = () => {
  return request({
    url: "/music/recommendations",
    method: "get",
  });
};

// 获取音乐URL
export const getMusicUrl = (id: number) => {
  return request<MusicUrlResponse>({
    url: `/music/song/url`,
    method: "get",
    params: { id },
  });
};

// 获取推荐歌单
export const getRecommendPlaylists =
  (): Promise<RecommendPlaylistsResponse> => {
    return request({
      url: "/music/personalized",
      method: "get",
    });
  };

// 获取歌曲详情
export const getSongDetail = (id: number) => {
  return request<SearchResponse>({
    url: "/music/song/detail",
    method: "get",
    params: { id },
  });
};
