<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- 欢迎卡片 -->
      <el-col :span="24">
        <el-card class="welcome-card">
          <div class="welcome-content">
            <div class="welcome-icon">
              <el-icon :size="48"><HomeFilled /></el-icon>
            </div>
            <div class="welcome-text">
              <h2>欢迎回来，{{ userStore.nickname || "用户" }}</h2>
              <p>今天是 {{ currentDate }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <!-- 数据统计卡片 -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409eff">
              <el-icon :size="24"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.notesCount }}</div>
              <div class="stat-label">笔记总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67c23a">
              <el-icon :size="24"><Folder /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.categoriesCount }}</div>
              <div class="stat-label">分类总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #e6a23c">
              <el-icon :size="24"><StarFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.favoriteNotesCount }}</div>
              <div class="stat-label">收藏笔记</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f56c6c">
              <el-icon :size="24"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.eventsCount }}</div>
              <div class="stat-label">日程数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <!-- 最近笔记 -->
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>最近笔记</span>
              <el-button type="primary" text @click="router.push('/notes')">
                查看全部
              </el-button>
            </div>
          </template>
          <div v-if="recentNotes.length">
            <el-timeline>
              <el-timeline-item
                v-for="note in recentNotes"
                :key="note.id"
                :timestamp="note.createdAt"
                placement="top"
              >
                <el-card>
                  <h4>{{ note.title }}</h4>
                  <p v-if="note.content" class="note-content">
                    {{ note.content }}
                  </p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>

      <!-- 近期活动 -->
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>近期活动</span>
              <el-button type="primary" text @click="router.push('/calendar')">
                查看全部
              </el-button>
            </div>
          </template>
          <div v-if="upcomingEvents.length">
            <el-timeline>
              <el-timeline-item
                v-for="event in upcomingEvents"
                :key="event.id"
                :timestamp="event.startTime"
                placement="top"
              >
                <el-card>
                  <h4>{{ event.title }}</h4>
                  <p v-if="event.content" class="event-content">
                    {{ event.content }}
                  </p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  HomeFilled,
  Document,
  Folder,
  StarFilled,
  Calendar,
} from "@element-plus/icons-vue";
import { useUserStore } from "@/stores/user";

// 用户信息
const userStore = useUserStore();
// 路由对象
const router = useRouter();

// 当前日期
const currentDate = new Date().toLocaleDateString("zh-CN", {
  year: "numeric",
  month: "long",
  day: "numeric",
  weekday: "long",
});

// 统计数据
const stats = reactive({
  notesCount: 0,
  categoriesCount: 0,
  favoriteNotesCount: 0,
  eventsCount: 0,
});

// 最近笔记
const recentNotes = ref([
  {
    id: 1,
    title: "项目计划",
    content: "完成Vue3 + Element Plus管理系统开发",
    createdAt: "2025-03-25 10:00",
  },
  {
    id: 2,
    title: "学习笔记",
    content: "Vue3组合式API使用总结",
    createdAt: "2025-03-24 16:30",
  },
]);

// 近期活动
const upcomingEvents = ref([
  {
    id: 1,
    title: "团队会议",
    content: "讨论下一阶段开发计划",
    startTime: "2025-03-26 14:00",
  },
  {
    id: 2,
    title: "代码评审",
    content: "对新功能进行代码审查",
    startTime: "2025-03-27 10:30",
  },
]);

// 加载数据
onMounted(() => {
  // 模拟从API获取数据
  stats.notesCount = 12;
  stats.categoriesCount = 5;
  stats.favoriteNotesCount = 3;
  stats.eventsCount = 8;

  // 实际项目中，这里应该调用API获取真实数据
  // fetchDashboardData()
});

// 实际项目中的API调用
// async function fetchDashboardData() {
//   try {
//     const res = await request.get('/dashboard/stats')
//     if (res.data) {
//       Object.assign(stats, res.data)
//     }
//
//     const notesRes = await request.get('/notes/recent')
//     if (notesRes.data) {
//       recentNotes.value = notesRes.data
//     }
//
//     const eventsRes = await request.get('/events/upcoming')
//     if (eventsRes.data) {
//       upcomingEvents.value = eventsRes.data
//     }
//   } catch (error) {
//     console.error('获取数据失败', error)
//   }
// }
</script>

<style scoped>
.dashboard-container {
  padding: 0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  margin: 0;
  overflow: hidden;
}

.welcome-card {
  margin-bottom: 20px;
  width: 100%;
}

.welcome-content {
  display: flex;
  align-items: center;
}

.welcome-icon {
  margin-right: 16px;
  color: #409eff;
}

.welcome-text h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.welcome-text p {
  margin: 8px 0 0 0;
  color: #606266;
}

.mt-20 {
  margin-top: 20px;
}

.stat-card {
  margin-bottom: 20px;
  height: 100%;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  color: #fff;
  margin-right: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.box-card {
  margin-bottom: 20px;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.note-content,
.event-content {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 5px 0 0 0;
  color: #606266;
}

.el-timeline-item {
  padding-bottom: 20px;
}

/* 确保所有行都撑满宽度 */
.el-row {
  width: 100%;
  margin-left: 0 !important;
  margin-right: 0 !important;
}

/* 确保所有卡片都撑满宽度 */
.el-card {
  width: 100%;
}

/* 修复列间距 */
.el-col {
  padding-right: 10px !important;
  padding-left: 10px !important;
  box-sizing: border-box;
}

/* 调整第一列和最后一列的边距 */
.el-col:first-child {
  padding-left: 0 !important;
}

.el-col:last-child {
  padding-right: 0 !important;
}
</style>
