<template>
  <div class="music-player">
    <div class="player-content">
      <div class="song-info">
        <img
          :src="currentSong.cover || '/default-cover.jpg'"
          class="cover-img"
        />
        <div class="song-details">
          <h3>{{ currentSong.name || "未播放" }}</h3>
          <p>{{ currentSong.artist || "未知歌手" }}</p>
        </div>
      </div>

      <div class="controls">
        <el-slider
          v-model="progress"
          :max="duration"
          @change="handleProgressChange"
          class="progress-bar"
        />
        <div class="time-info">
          <span>{{ formatTime(currentTime) }}</span>
          <span>{{ formatTime(duration) }}</span>
        </div>
        <div class="control-buttons">
          <el-button circle @click="handlePrev">
            <el-icon><CaretLeft /></el-icon>
          </el-button>
          <el-button circle @click="togglePlay">
            <el-icon>
              <component :is="isPlaying ? 'Pause' : 'VideoPlay'" />
            </el-icon>
          </el-button>
          <el-button circle @click="handleNext">
            <el-icon><CaretRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import {
  CaretLeft,
  CaretRight,
  Pause,
  VideoPlay,
} from "@element-plus/icons-vue";

interface Song {
  id: number;
  name: string;
  artist: string;
  cover: string;
  url: string;
}

const currentSong = ref<Song>({
  id: 0,
  name: "",
  artist: "",
  cover: "",
  url: "",
});

const isPlaying = ref(false);
const progress = ref(0);
const duration = ref(0);
const currentTime = ref(0);
const audio = new Audio();

// 播放控制
const togglePlay = () => {
  if (isPlaying.value) {
    audio.pause();
  } else {
    audio.play();
  }
  isPlaying.value = !isPlaying.value;
};

const handlePrev = () => {
  // 实现上一首
};

const handleNext = () => {
  // 实现下一首
};

const handleProgressChange = (value: number) => {
  audio.currentTime = value;
  currentTime.value = value;
};

// 格式化时间
const formatTime = (time: number) => {
  const minutes = Math.floor(time / 60);
  const seconds = Math.floor(time % 60);
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
};

// 监听音频事件
audio.addEventListener("timeupdate", () => {
  currentTime.value = audio.currentTime;
  progress.value = audio.currentTime;
});

audio.addEventListener("loadedmetadata", () => {
  duration.value = audio.duration;
});

// 导出方法供父组件调用
defineExpose({
  play: (song: Song) => {
    currentSong.value = song;
    audio.src = song.url;
    audio.play();
    isPlaying.value = true;
  },
  pause: () => {
    audio.pause();
    isPlaying.value = false;
  },
});
</script>

<style scoped>
.music-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  padding: 10px 20px;
  z-index: 1000;
}

.player-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
}

.song-info {
  display: flex;
  align-items: center;
  width: 300px;
}

.cover-img {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  margin-right: 15px;
}

.song-details {
  flex: 1;
}

.song-details h3 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.song-details p {
  margin: 5px 0 0;
  font-size: 12px;
  color: #999;
}

.controls {
  flex: 1;
  margin-left: 20px;
}

.progress-bar {
  margin-bottom: 10px;
}

.time-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-bottom: 10px;
}

.control-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}
</style>
