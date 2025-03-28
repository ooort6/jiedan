import request from "@/utils/request";
import type {
  SearchResponse,
  PlaylistDetailResponse,
  MusicUrlResponse,
  RecommendPlaylistsResponse,
} from "@/types/music";

// 搜索音乐
export const searchMusic = (
  keywords: string,
  type: number = 1,
  limit: number = 30
) => {
  return request<SearchResponse>({
    url: "/api/music/search",
    method: "get",
    params: {
      keywords,
      type,
      limit,
    },
  });
};

// 获取歌单详情
export const getPlaylistDetail = (id: number) => {
  return request<PlaylistDetailResponse>({
    url: `/api/music/playlist/detail`,
    method: "get",
    params: { id },
  });
};

// 获取音乐URL
export const getMusicUrl = (id: number) => {
  return request<MusicUrlResponse>({
    url: `/api/music/song/url`,
    method: "get",
    params: { id },
  });
};

// 获取推荐歌单
export const getRecommendPlaylists = (limit: number = 30) => {
  return request<RecommendPlaylistsResponse>({
    url: "/api/music/personalized",
    method: "get",
    params: { limit },
  });
};

// 获取歌曲详情
export const getSongDetail = (ids: string) => {
  return request<SearchResponse>({
    url: "/api/music/song/detail",
    method: "get",
    params: { ids },
  });
};
