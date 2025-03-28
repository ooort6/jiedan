<template>
  <div class="music-container">
    <el-row :gutter="20">
      <!-- 左侧菜单 -->
      <el-col :span="4">
        <el-card class="menu-card">
          <el-menu
            default-active="search"
            class="music-menu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="search">
              <el-icon><Search /></el-icon>
              <span>音乐搜索</span>
            </el-menu-item>
            <el-menu-item index="playlist">
              <el-icon><List /></el-icon>
              <span>我的歌单</span>
            </el-menu-item>
            <el-menu-item index="favorites">
              <el-icon><Star /></el-icon>
              <span>我的收藏</span>
            </el-menu-item>
            <el-menu-item index="recommend">
              <el-icon><Promotion /></el-icon>
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
          <div class="card-header">
            <el-tabs v-model="activeTab">
              <el-tab-pane label="单曲" name="songs">
                <div class="song-list">
                  <div v-for="song in songs" :key="song.id" class="song-item">
                    <div class="song-info" @click="playSong(song)">
                      <img :src="song.cover" class="song-cover" />
                      <div class="song-details">
                        <h4>{{ song.name }}</h4>
                        <p>{{ song.artist }}</p>
                      </div>
                    </div>
                    <div class="song-actions">
                      <el-button
                        :type="isFavorite(song.id) ? 'danger' : 'default'"
                        :icon="isFavorite(song.id) ? 'Star' : 'StarFilled'"
                        circle
                        @click="toggleFavorite(song)"
                      />
                      <el-button
                        type="primary"
                        :icon="
                          song.id === currentSong?.id
                            ? 'VideoPause'
                            : 'VideoPlay'
                        "
                        circle
                        @click="playSong(song)"
                      />
                      <el-button
                        icon="Plus"
                        circle
                        @click="addToPlaylist(song)"
                      />
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
                    <div class="playlist-cover-container">
                      <img :src="playlist.cover" class="playlist-cover" />
                      <div class="playlist-hover-overlay">
                        <el-button type="primary" circle icon="VideoPlay" />
                      </div>
                    </div>
                    <h4>{{ playlist.name }}</h4>
                    <p>{{ playlist.trackCount }}首</p>
                  </el-card>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>

        <!-- 播放列表抽屉 -->
        <el-drawer
          v-model="showPlaylist"
          title="播放列表"
          direction="rtl"
          size="400px"
        >
          <div class="playlist-drawer">
            <div
              v-for="(song, index) in playQueue"
              :key="song.id"
              :class="['queue-item', { active: song.id === currentSong?.id }]"
              @click="playSong(song)"
            >
              <span class="queue-index">{{ index + 1 }}</span>
              <div class="queue-info">
                <h4>{{ song.name }}</h4>
                <p>{{ song.artist }}</p>
              </div>
              <el-button
                type="danger"
                icon="Delete"
                circle
                @click.stop="removeFromQueue(index)"
              />
            </div>
          </div>
        </el-drawer>
      </el-col>
    </el-row>

    <!-- 音乐播放器组件 -->
    <MusicPlayer ref="musicPlayer" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import {
  Search,
  List,
  Star,
  Promotion,
  VideoPlay,
  VideoPause,
  Plus,
  StarFilled,
  Delete,
} from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import MusicPlayer from "@/components/MusicPlayer.vue";
import {
  searchMusic,
  getPlaylistDetail,
  getMusicUrl,
  getRecommendPlaylists,
  getSongDetail,
} from "@/api/music";
import type {
  Song,
  Playlist,
  SearchResponse,
  PlaylistDetailResponse,
} from "@/types/music";

interface DisplaySong {
  id: number;
  name: string;
  title: string;
  artist: string;
  album: string;
  duration: number;
  cover: string;
  cover_url: string;
  source_url: string;
  url?: string;
}

interface DisplayPlaylist {
  id: number;
  name: string;
  description: string;
  cover: string;
  cover_url: string;
  created_at: string;
  song_count: number;
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

// 播放队列
const playQueue = ref<DisplaySong[]>([]);
const currentSong = ref<DisplaySong | null>(null);
const showPlaylist = ref(false);

// 收藏列表
const favorites = ref<DisplaySong[]>([]);

// 当前菜单
const currentMenu = ref("search");

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  currentMenu.value = index;
  switch (index) {
    case "favorites":
      loadFavorites();
      break;
    case "recommend":
      loadRecommendSongs();
      break;
    case "playlist":
      loadUserPlaylists();
      break;
  }
};

// 加载收藏
const loadFavorites = () => {
  // 从本地存储加载收藏
  const savedFavorites = localStorage.getItem("favorites");
  if (savedFavorites) {
    favorites.value = JSON.parse(savedFavorites);
  }
};

// 检查是否收藏
const isFavorite = (songId: number) => {
  return favorites.value.some((song) => song.id === songId);
};

// 切换收藏状态
const toggleFavorite = (song: DisplaySong) => {
  const index = favorites.value.findIndex((f) => f.id === song.id);
  if (index === -1) {
    favorites.value.push(song);
    ElMessage.success("已添加到收藏");
  } else {
    favorites.value.splice(index, 1);
    ElMessage.success("已取消收藏");
  }
  localStorage.setItem("favorites", JSON.stringify(favorites.value));
};

// 添加到播放列表
const addToPlaylist = (song: DisplaySong) => {
  if (!playQueue.value.some((s) => s.id === song.id)) {
    playQueue.value.push(song);
    ElMessage.success("已添加到播放列表");
  }
};

// 从播放列表移除
const removeFromQueue = (index: number) => {
  playQueue.value.splice(index, 1);
};

// 处理搜索
const handleSearch = async () => {
  if (!searchQuery.value) {
    ElMessage.warning("请输入搜索关键词");
    return;
  }

  loading.value = true;
  try {
    console.log("开始搜索，关键词：", searchQuery.value);
    const data = await searchMusic(searchQuery.value);
    console.log("搜索结果：", data);
    if (data && data.songs && data.songs.length > 0) {
      songs.value = data.songs.map((song: Song) => ({
        ...song,
        name: song.title,
        cover: song.cover_url,
        url: undefined,
      }));
      console.log("处理后的歌曲列表：", songs.value);
    } else {
      console.log("没有找到匹配的歌曲");
      songs.value = [];
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
      currentSong.value = song;
      if (!playQueue.value.some((s) => s.id === song.id)) {
        playQueue.value.push(song);
      }
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
    const data = await getPlaylistDetail(playlist.id);
    if (data && data.songs) {
      songs.value = data.songs.map((song: Song) => ({
        ...song,
        name: song.title,
        cover: song.cover_url,
        url: undefined,
      }));
      activeTab.value = "songs";
    }
  } catch (error) {
    console.error("获取歌单详情失败:", error);
    ElMessage.error("获取歌单详情失败，请稍后重试");
  }
};

// 加载推荐歌曲
const loadRecommendSongs = async () => {
  try {
    const data = await getRecommendPlaylists();
    if (data && data.result && data.result.length > 0) {
      const songPromises = data.result
        .slice(0, 3)
        .map(async (playlist: Playlist) => {
          const detail = await getPlaylistDetail(playlist.id);
          return detail?.songs?.slice(0, 10) || [];
        });
      const playlistSongs = await Promise.all(songPromises);
      songs.value = playlistSongs.flat().map((track: any) => ({
        id: track.id,
        title: track.name,
        name: track.name,
        artist: track.ar.map((a: any) => a.name).join("/"),
        album: track.al.name,
        cover: track.al.picUrl,
        cover_url: track.al.picUrl,
        source_url: "",
        duration: Math.floor(track.dt / 1000),
      }));
    }
  } catch (error) {
    console.error("获取推荐歌曲失败:", error);
    ElMessage.error("获取推荐歌曲失败，请稍后重试");
  }
};

// 加载用户歌单
const loadUserPlaylists = async () => {
  try {
    // 这里应该调用获取用户歌单的API
    // 暂时显示本地存储的收藏歌曲作为示例
    const savedFavorites = localStorage.getItem("favorites");
    if (savedFavorites) {
      const favoriteSongs = JSON.parse(savedFavorites);
      songs.value = favoriteSongs;
    }
  } catch (error) {
    console.error("获取用户歌单失败:", error);
    ElMessage.error("获取用户歌单失败，请稍后重试");
  }
};

// 格式化时长
const formatDuration = (seconds: number) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
};

// 组件挂载时加载数据
onMounted(() => {
  loadRecommendSongs();
  loadFavorites();
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

.song-actions {
  display: flex;
  gap: 10px;
}

.queue-item {
  display: flex;
  align-items: center;
  padding: 10px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.queue-item:hover {
  background-color: #f5f7fa;
}

.queue-item.active {
  background-color: #ecf5ff;
}

.queue-index {
  width: 30px;
  text-align: center;
  color: #999;
}

.queue-info {
  flex: 1;
  margin: 0 15px;
}

.queue-info h4 {
  margin: 0;
  font-size: 14px;
}

.queue-info p {
  margin: 5px 0 0;
  font-size: 12px;
  color: #999;
}

.playlist-cover-container {
  position: relative;
  overflow: hidden;
  border-radius: 4px;
}

.playlist-hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.playlist-card:hover .playlist-hover-overlay {
  opacity: 1;
}

.card-header {
  margin-bottom: 20px;
}
</style>
