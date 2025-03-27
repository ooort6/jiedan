<template>
  <div class="chat-container">
    <!-- 标题栏 -->
    <div class="chat-header">
      <h2>AI 助手</h2>
      <el-button type="danger" plain @click="clearHistory">
        清空对话
      </el-button>
    </div>

    <!-- 聊天记录区域 -->
    <div class="chat-messages" ref="messagesRef">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="[
          'message',
          message.role === 'user' ? 'message-user' : 'message-ai',
        ]"
      >
        <div class="message-avatar">
          <el-avatar
            :size="40"
            :src="message.role === 'user' ? userAvatar : aiAvatar"
          />
        </div>
        <div class="message-content">
          <div
            class="message-text"
            v-html="formatMessage(message.content)"
          ></div>
          <div class="message-time">{{ formatTime(message.time) }}</div>
        </div>
      </div>
      <!-- 加载状态 -->
      <div v-if="loading" class="message message-ai">
        <div class="message-avatar">
          <el-avatar :size="40" :src="aiAvatar" />
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="输入您的问题..."
        @keyup.enter.exact.prevent="sendMessage"
      />
      <el-button type="primary" :loading="loading" @click="sendMessage">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from "vue";
import { useUserStore } from "@/stores/user";
import { marked } from "marked";
import hljs from "highlight.js";
import "highlight.js/styles/github.css";
import deepseekService from "@/api/deepseek";
import { ElMessage } from "element-plus";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  time: number;
}

// 状态
const messages = ref<ChatMessage[]>([]);
const inputMessage = ref("");
const loading = ref(false);
const messagesRef = ref<HTMLElement | null>(null);

// 用户信息
const userStore = useUserStore();
const userAvatar =
  userStore.avatar ||
  "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png";
const aiAvatar = "https://www.deepseek.com/favicon.ico";

// 保存聊天记录到本地存储
const saveChatHistory = () => {
  localStorage.setItem(
    `chat_history_${userStore.username}`,
    JSON.stringify(messages.value)
  );
};

// 从本地存储加载聊天记录
const loadChatHistory = () => {
  const history = localStorage.getItem(`chat_history_${userStore.username}`);
  if (history) {
    messages.value = JSON.parse(history);
  } else {
    // 如果没有历史记录，显示欢迎消息
    messages.value = [
      {
        role: "assistant",
        content: "你好！我是 AI 助手，有什么我可以帮你的吗？",
        time: Date.now(),
      },
    ];
  }
};

// 清空聊天记录
const clearHistory = () => {
  messages.value = [
    {
      role: "assistant",
      content: "聊天记录已清空，有什么我可以帮你的吗？",
      time: Date.now(),
    },
  ];
};

// 监听消息变化，自动保存
watch(
  messages,
  () => {
    saveChatHistory();
  },
  { deep: true }
);

// 格式化消息内容（支持 Markdown）
const formatMessage = (content: string) => {
  marked.setOptions({
    highlight: (code: string, language: string) => {
      if (language && hljs.getLanguage(language)) {
        try {
          return hljs.highlight(code, { language }).value;
        } catch (err) {
          console.error("Highlight error:", err);
        }
      }
      return hljs.highlightAuto(code).value;
    },
    langPrefix: "hljs language-",
  } as marked.MarkedOptions);

  return marked(content);
};

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("zh-CN", { hour12: false });
};

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return;

  const userMessage = inputMessage.value;
  messages.value.push({
    role: "user",
    content: userMessage,
    time: Date.now(),
  });

  inputMessage.value = "";
  loading.value = true;

  try {
    const response = await deepseekService.chat(
      messages.value.map(({ role, content }) => ({ role, content }))
    );

    if (response.error) {
      throw new Error(response.error);
    }

    messages.value.push({
      role: "assistant",
      content: response.message,
      time: Date.now(),
    });
  } catch (error: any) {
    console.error("Error:", error);
    ElMessage.error(error.message || "请求失败，请稍后重试");
    messages.value.push({
      role: "assistant",
      content: "抱歉，我遇到了一些问题，请稍后再试。",
      time: Date.now(),
    });
  } finally {
    loading.value = false;
    await nextTick();
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
    }
  }
};

// 组件挂载时加载历史记录
onMounted(() => {
  loadChatHistory();
});
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.chat-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.message {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.message-user {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 12px;
}

.message-content {
  max-width: 70%;
  background: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-user .message-content {
  background: #409eff;
  color: #fff;
}

.message-text {
  line-height: 1.5;
  white-space: pre-wrap;
}

.message-user .message-text :deep(code) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.message-user .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.chat-input {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.chat-input :deep(.el-textarea__inner) {
  resize: none;
  border-radius: 8px;
}

.chat-input .el-button {
  height: 82px;
  width: 80px;
}

/* 打字动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #409eff;
  border-radius: 50%;
  animation: typing 1s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}
.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

/* Markdown 样式 */
.message-content :deep(pre) {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

.message-content :deep(code) {
  background: #f0f2f5;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

.message-content :deep(p) {
  margin: 8px 0;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  padding-left: 20px;
}
</style>
