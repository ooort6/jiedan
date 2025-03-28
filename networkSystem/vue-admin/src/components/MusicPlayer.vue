<template>
  <div class="music-player" :class="{ 'is-playing': isPlaying }">
    <audio
      ref="audioPlayer"
      :src="currentSong?.source_url"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
      @canplay="onCanPlay"
    ></audio>

    <div class="player-content">
      <!-- 歌曲信息 -->
      <div class="song-info">
        <img
          v-if="currentSong?.cover_url"
          :src="currentSong.cover_url"
          class="cover-image"
          :class="{ rotating: isPlaying }"
        />
        <div class="song-details">
          <h3>{{ currentSong?.title || "未播放" }}</h3>
          <p>{{ currentSong?.artist || "暂无歌手" }}</p>
        </div>
      </div>

      <!-- 播放控制 -->
      <div class="player-controls">
        <el-button
          circle
          :icon="isPlaying ? 'VideoPause' : 'VideoPlay'"
          @click="togglePlay"
        />
        <div class="progress-bar">
          <el-slider
            v-model="currentTime"
            :max="duration"
            :format-tooltip="formatTime"
            @change="onProgressChange"
          />
          <div class="time-info">
            <span>{{ formatTime(currentTime) }}</span>
            <span>{{ formatTime(duration) }}</span>
          </div>
        </div>
      </div>

      <!-- 音量控制 -->
      <div class="volume-control">
        <el-button
          circle
          :icon="volume === 0 ? 'Mute' : 'Microphone'"
          @click="toggleMute"
        />
        <el-slider v-model="volume" :max="100" class="volume-slider" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import {
  VideoPause,
  VideoPlay,
  Microphone,
  Mute,
} from "@element-plus/icons-vue";
import type { Song } from "@/api/music";

const audioPlayer = ref<HTMLAudioElement | null>(null);
const currentSong = ref<Song | null>(null);
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(50);
const previousVolume = ref(50);

// 播放新歌曲
const play = (song: Song) => {
  currentSong.value = song;
  if (audioPlayer.value) {
    audioPlayer.value.load();
    audioPlayer.value.play();
    isPlaying.value = true;
  }
};

// 切换播放/暂停
const togglePlay = () => {
  if (!audioPlayer.value || !currentSong.value) return;

  if (isPlaying.value) {
    audioPlayer.value.pause();
  } else {
    audioPlayer.value.play();
  }
  isPlaying.value = !isPlaying.value;
};

// 切换静音
const toggleMute = () => {
  if (!audioPlayer.value) return;

  if (volume.value === 0) {
    volume.value = previousVolume.value;
  } else {
    previousVolume.value = volume.value;
    volume.value = 0;
  }
  audioPlayer.value.volume = volume.value / 100;
};

// 更新进度
const onTimeUpdate = () => {
  if (!audioPlayer.value) return;
  currentTime.value = Math.floor(audioPlayer.value.currentTime);
};

// 歌曲结束
const onEnded = () => {
  isPlaying.value = false;
  currentTime.value = 0;
  // 这里可以添加自动播放下一首的逻辑
};

// 歌曲可以播放时
const onCanPlay = () => {
  if (!audioPlayer.value) return;
  duration.value = Math.floor(audioPlayer.value.duration);
};

// 进度条改变
const onProgressChange = (value: number) => {
  if (!audioPlayer.value) return;
  audioPlayer.value.currentTime = value;
};

// 格式化时间
const formatTime = (seconds: number) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
};

// 监听音量变化
const watchVolume = () => {
  if (!audioPlayer.value) return;
  audioPlayer.value.volume = volume.value / 100;
};

// 组件挂载时
onMounted(() => {
  if (audioPlayer.value) {
    audioPlayer.value.volume = volume.value / 100;
  }
});

// 组件卸载时
onUnmounted(() => {
  if (audioPlayer.value) {
    audioPlayer.value.pause();
  }
});

// 导出方法供父组件使用
defineExpose({
  play,
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
  gap: 15px;
  width: 300px;
}

.cover-image {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  object-fit: cover;
}

.rotating {
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.song-details {
  overflow: hidden;
}

.song-details h3 {
  margin: 0;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.song-details p {
  margin: 5px 0 0;
  font-size: 12px;
  color: #999;
}

.player-controls {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 50px;
}

.progress-bar {
  flex: 1;
}

.time-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 200px;
}

.volume-slider {
  width: 100px;
}
</style>
