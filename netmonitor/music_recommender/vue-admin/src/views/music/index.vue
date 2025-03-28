<template>
  <div class="music-container">
    <el-row :gutter="20">
      <!-- 左侧菜单 -->
      <el-col :span="4">
        <el-card class="menu-card">
          <el-menu default-active="search" class="music-menu">
            <el-menu-item index="search">
              <el-icon><Search /></el-icon>
              <span>音乐搜索</span>
            </el-menu-item>
            <el-menu-item index="playlist">
              <el-icon><List /></el-icon>
              <span>我的歌单</span>
            </el-menu-item>
            <el-menu-item index="recommend">
              <el-icon><Star /></el-icon>
              <span>推荐歌曲</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <!-- 主内容区 -->
      <el-col :span="20">
        <!-- 搜索框 -->
        <el-card class="search-card">
          <el-input
            v-model="searchQuery"
            placeholder="搜索音乐、歌手、歌单"
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-card>

        <!-- 搜索结果/歌单列表 -->
        <el-card class="content-card">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="单曲" name="songs">
              <div class="song-list">
                <div
                  v-for="song in songs"
                  :key="song.id"
                  class="song-item"
                  @click="playSong(song)"
                >
                  <div class="song-info">
                    <img :src="song.cover" class="song-cover" />
                    <div class="song-details">
                      <h4>{{ song.name }}</h4>
                      <p>{{ song.artist }}</p>
                    </div>
                  </div>
                  <div class="song-duration">
                    {{ formatDuration(song.duration) }}
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="歌单" name="playlists">
              <div class="playlist-grid">
                <el-card
                  v-for="playlist in playlists"
                  :key="playlist.id"
                  class="playlist-card"
                  @click="openPlaylist(playlist)"
                >
                  <img :src="playlist.cover" class="playlist-cover" />
                  <h4>{{ playlist.name }}</h4>
                  <p>{{ playlist.trackCount }}首</p>
                </el-card>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 音乐播放器组件 -->
    <MusicPlayer ref="musicPlayer" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Search, List, Star } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import MusicPlayer from "@/components/MusicPlayer.vue";
import {
  searchMusic,
  getPlaylistDetail,
  getMusicUrl,
  getRecommendPlaylists,
  getSongDetail,
} from "@/api/music";
import type { Song, Playlist } from "@/types/music";

interface DisplaySong {
  id: number;
  name: string;
  artist: string;
  cover: string;
  duration: number;
  url?: string;
}

interface DisplayPlaylist {
  id: number;
  name: string;
  cover: string;
  trackCount: number;
}

// 搜索相关
const searchQuery = ref("");
const activeTab = ref("songs");
const loading = ref(false);

// 数据
const songs = ref<DisplaySong[]>([]);
const playlists = ref<DisplayPlaylist[]>([]);

// 音乐播放器引用
const musicPlayer = ref();

// 处理搜索
const handleSearch = async () => {
  if (!searchQuery.value) {
    ElMessage.warning("请输入搜索关键词");
    return;
  }

  loading.value = true;
  try {
    const { data: res } = await searchMusic(searchQuery.value);
    if (activeTab.value === "songs" && res.result.songs) {
      songs.value = res.result.songs.map((song: Song) => ({
        id: song.id,
        name: song.name,
        artist: song.artists.map((a) => a.name).join("/"),
        cover: song.album.picUrl,
        duration: Math.floor(song.duration / 1000),
      }));
    } else {
      const { data: playlistRes } = await searchMusic(searchQuery.value, 1000);
      if (playlistRes.result.playlists) {
        playlists.value = playlistRes.result.playlists.map(
          (playlist: Playlist) => ({
            id: playlist.id,
            name: playlist.name,
            cover: playlist.coverImgUrl,
            trackCount: playlist.trackCount,
          })
        );
      }
    }
  } catch (error) {
    console.error("搜索失败:", error);
    ElMessage.error("搜索失败，请稍后重试");
  } finally {
    loading.value = false;
  }
};

// 播放音乐
const playSong = async (song: DisplaySong) => {
  try {
    const { data: urlRes } = await getMusicUrl(song.id);
    if (urlRes.data[0]?.url) {
      song.url = urlRes.data[0].url;
      musicPlayer.value?.play(song);
    } else {
      ElMessage.warning("暂无版权或VIP专属");
    }
  } catch (error) {
    console.error("获取音乐URL失败:", error);
    ElMessage.error("播放失败，请稍后重试");
  }
};

// 打开歌单
const openPlaylist = async (playlist: DisplayPlaylist) => {
  try {
    const { data: res } = await getPlaylistDetail(playlist.id);
    if (res.playlist.tracks) {
      songs.value = res.playlist.tracks.map((track) => ({
        id: track.id,
        name: track.name,
        artist: track.ar.map((a) => a.name).join("/"),
        cover: track.al.picUrl,
        duration: Math.floor(track.dt / 1000),
      }));
      activeTab.value = "songs";
    }
  } catch (error) {
    console.error("获取歌单详情失败:", error);
    ElMessage.error("获取歌单详情失败，请稍后重试");
  }
};

// 获取推荐歌单
const loadRecommendPlaylists = async () => {
  try {
    const { data: res } = await getRecommendPlaylists();
    playlists.value = res.result.map((playlist: Playlist) => ({
      id: playlist.id,
      name: playlist.name,
      cover: playlist.coverImgUrl,
      trackCount: playlist.trackCount,
    }));
  } catch (error) {
    console.error("获取推荐歌单失败:", error);
    ElMessage.error("获取推荐歌单失败，请稍后重试");
  }
};

// 格式化时长
const formatDuration = (seconds: number) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
};

// 组件挂载时加载推荐歌单
onMounted(() => {
  loadRecommendPlaylists();
});
</script>

<style scoped>
.music-container {
  padding-bottom: 100px; /* 为播放器留出空间 */
}

.menu-card,
.search-card,
.content-card {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
}

.song-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.song-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.song-item:hover {
  background-color: #f5f7fa;
}

.song-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.song-cover {
  width: 40px;
  height: 40px;
  border-radius: 4px;
}

.song-details h4 {
  margin: 0;
  font-size: 14px;
}

.song-details p {
  margin: 5px 0 0;
  font-size: 12px;
  color: #999;
}

.song-duration {
  color: #999;
  font-size: 12px;
}

.playlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
  padding: 10px;
}

.playlist-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.playlist-card:hover {
  transform: translateY(-5px);
}

.playlist-cover {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 10px;
}

.playlist-card h4 {
  margin: 0;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.playlist-card p {
  margin: 5px 0 0;
  font-size: 12px;
  color: #999;
}
</style>
