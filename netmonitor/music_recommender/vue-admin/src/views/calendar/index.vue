<template>
  <div class="calendar-container">
    <el-row :gutter="20">
      <!-- 左侧日历 -->
      <el-col :xs="24" :sm="16" :md="17" :lg="18">
        <el-card class="calendar-card">
          <template #header>
            <div class="card-header">
              <div class="date-nav">
                <el-button @click="goToday">今天</el-button>
                <el-button-group>
                  <el-button @click="prevMonth">
                    <el-icon><ArrowLeft /></el-icon>
                  </el-button>
                  <el-button @click="nextMonth">
                    <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </el-button-group>
                <span class="current-date">{{ displayDate }}</span>
              </div>

              <el-button type="primary" @click="handleCreateEvent">
                <el-icon><Plus /></el-icon> 添加事件
              </el-button>
            </div>
          </template>

          <el-calendar v-model="currentDate">
            <template #dateCell="{ data }">
              <div class="calendar-cell">
                <p class="day">{{ data.day.split("-").slice(2)[0] }}</p>

                <div class="event-list">
                  <div
                    v-for="event in getEventsOnDate(data)"
                    :key="event.id"
                    class="event-item"
                    :class="getEventClass(event)"
                    @click="handleViewEvent(event)"
                  >
                    {{ event.title }}
                  </div>
                </div>
              </div>
            </template>
          </el-calendar>
        </el-card>
      </el-col>

      <!-- 右侧事件列表 -->
      <el-col :xs="24" :sm="8" :md="7" :lg="6">
        <el-card class="events-card">
          <template #header>
            <div class="card-header">
              <span>近期事件</span>
              <el-radio-group v-model="eventFilter" size="small">
                <el-radio-button label="upcoming">即将</el-radio-button>
                <el-radio-button label="all">全部</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <el-empty v-if="filteredEvents.length === 0" description="暂无事件" />

          <el-timeline v-else>
            <el-timeline-item
              v-for="event in filteredEvents"
              :key="event.id"
              :timestamp="formatDateTime(event.startTime)"
              :type="getEventTimelineType(event)"
            >
              <el-card
                shadow="hover"
                class="event-card"
                @click="handleViewEvent(event)"
              >
                <h4>{{ event.title }}</h4>
                <p v-if="event.content" class="event-desc">
                  {{ event.content }}
                </p>
                <div class="event-time">
                  {{ formatTime(event.startTime) }} -
                  {{ formatTime(event.endTime) }}
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- 事件对话框 -->
    <el-dialog
      v-model="eventDialogVisible"
      :title="isEdit ? '编辑事件' : '新建事件'"
      width="600px"
      destroy-on-close
    >
      <el-form
        :model="eventForm"
        label-width="80px"
        ref="eventFormRef"
        :rules="eventRules"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="eventForm.title" placeholder="请输入事件标题" />
        </el-form-item>

        <el-form-item label="开始时间" prop="startTime">
          <el-date-picker
            v-model="eventForm.startTime"
            type="datetime"
            placeholder="选择开始时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm"
          />
        </el-form-item>

        <el-form-item label="结束时间" prop="endTime">
          <el-date-picker
            v-model="eventForm.endTime"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm"
          />
        </el-form-item>

        <el-form-item label="类型" prop="type">
          <el-select v-model="eventForm.type" placeholder="请选择事件类型">
            <el-option label="会议" value="meeting" />
            <el-option label="出差" value="trip" />
            <el-option label="个人" value="personal" />
            <el-option label="休假" value="vacation" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="eventForm.status">
            <el-radio label="pending">未开始</el-radio>
            <el-radio label="ongoing">进行中</el-radio>
            <el-radio label="completed">已完成</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="eventForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入事件详情"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="eventDialogVisible = false">取消</el-button>
        <el-button v-if="isEdit" type="danger" @click="handleDeleteEvent"
          >删除</el-button
        >
        <el-button type="primary" @click="handleSaveEvent">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import { ArrowLeft, ArrowRight, Plus } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox, FormInstance, FormRules } from "element-plus";
import dayjs from "dayjs";

// 数据类型定义
interface Event {
  id: number;
  title: string;
  content: string;
  startTime: string;
  endTime: string;
  type: "meeting" | "trip" | "personal" | "vacation" | "other";
  status: "pending" | "ongoing" | "completed";
}

// 日历相关
const currentDate = ref(new Date());

// 获取当前显示的年月
const displayDate = computed(() => {
  return dayjs(currentDate.value).format("YYYY年MM月");
});

// 日历导航
const goToday = () => {
  currentDate.value = new Date();
};

const prevMonth = () => {
  const date = dayjs(currentDate.value).subtract(1, "month");
  currentDate.value = date.toDate();
};

const nextMonth = () => {
  const date = dayjs(currentDate.value).add(1, "month");
  currentDate.value = date.toDate();
};

// 事件列表
const events = ref<Event[]>([
  {
    id: 1,
    title: "项目启动会议",
    content: "讨论新项目的需求和技术方案",
    startTime: "2025-03-26 09:00",
    endTime: "2025-03-26 10:30",
    type: "meeting",
    status: "pending",
  },
  {
    id: 2,
    title: "产品评审",
    content: "评审产品原型和设计稿",
    startTime: "2025-03-27 14:00",
    endTime: "2025-03-27 16:00",
    type: "meeting",
    status: "pending",
  },
  {
    id: 3,
    title: "团队建设活动",
    content: "团队户外拓展训练",
    startTime: "2025-03-30 09:00",
    endTime: "2025-03-30 17:00",
    type: "personal",
    status: "pending",
  },
  {
    id: 4,
    title: "代码评审",
    content: "评审登录模块代码",
    startTime: "2025-03-28 10:00",
    endTime: "2025-03-28 11:30",
    type: "meeting",
    status: "pending",
  },
  {
    id: 5,
    title: "项目交付",
    content: "第一阶段功能交付",
    startTime: "2025-04-10 16:00",
    endTime: "2025-04-10 17:30",
    type: "meeting",
    status: "pending",
  },
]);

// 根据日期获取事件
const getEventsOnDate = (data: any) => {
  const date = data.day;
  return events.value.filter(
    (event) =>
      event.startTime.startsWith(date) ||
      (event.startTime < date && event.endTime > date)
  );
};

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  return dayjs(dateStr).format("MM-DD HH:mm");
};

// 格式化时间
const formatTime = (dateStr: string) => {
  return dayjs(dateStr).format("HH:mm");
};

// 获取事件的CSS类
const getEventClass = (event: Event) => {
  return {
    "event-meeting": event.type === "meeting",
    "event-trip": event.type === "trip",
    "event-personal": event.type === "personal",
    "event-vacation": event.type === "vacation",
    "event-other": event.type === "other",
    "event-completed": event.status === "completed",
  };
};

// 获取事件时间线类型
const getEventTimelineType = (event: Event) => {
  switch (event.type) {
    case "meeting":
      return "primary";
    case "trip":
      return "warning";
    case "personal":
      return "success";
    case "vacation":
      return "info";
    default:
      return "";
  }
};

// 事件过滤
const eventFilter = ref("upcoming");
const filteredEvents = computed(() => {
  if (eventFilter.value === "upcoming") {
    const now = dayjs().format("YYYY-MM-DD HH:mm");
    return events.value
      .filter((event) => event.startTime >= now || event.status === "ongoing")
      .sort((a, b) => dayjs(a.startTime).diff(dayjs(b.startTime)))
      .slice(0, 5);
  } else {
    return [...events.value].sort((a, b) =>
      dayjs(a.startTime).diff(dayjs(b.startTime))
    );
  }
});

// 事件对话框
const eventDialogVisible = ref(false);
const isEdit = ref(false);
const eventFormRef = ref<FormInstance>();
const eventForm = reactive({
  id: 0,
  title: "",
  content: "",
  startTime: "",
  endTime: "",
  type: "meeting" as const,
  status: "pending" as const,
});

// 表单验证规则
const eventRules: FormRules = {
  title: [
    { required: true, message: "请输入事件标题", trigger: "blur" },
    { max: 50, message: "标题长度不能超过50个字符", trigger: "blur" },
  ],
  startTime: [{ required: true, message: "请选择开始时间", trigger: "change" }],
  endTime: [
    { required: true, message: "请选择结束时间", trigger: "change" },
    {
      validator: (rule, value, callback) => {
        if (value && eventForm.startTime && value <= eventForm.startTime) {
          callback(new Error("结束时间必须晚于开始时间"));
        } else {
          callback();
        }
      },
      trigger: "change",
    },
  ],
  type: [{ required: true, message: "请选择事件类型", trigger: "change" }],
};

// 新建事件
const handleCreateEvent = () => {
  isEdit.value = false;
  eventForm.id = 0;
  eventForm.title = "";
  eventForm.content = "";

  // 默认设置开始时间为当前所选日期的上午9点
  const today = dayjs().format("YYYY-MM-DD");
  eventForm.startTime = `${today} 09:00`;
  eventForm.endTime = `${today} 10:00`;

  eventForm.type = "meeting";
  eventForm.status = "pending";
  eventDialogVisible.value = true;
};

// 查看/编辑事件
const handleViewEvent = (event: Event) => {
  isEdit.value = true;
  eventForm.id = event.id;
  eventForm.title = event.title;
  eventForm.content = event.content;
  eventForm.startTime = event.startTime;
  eventForm.endTime = event.endTime;
  eventForm.type = event.type;
  eventForm.status = event.status;
  eventDialogVisible.value = true;
};

// 保存事件
const handleSaveEvent = async () => {
  if (!eventFormRef.value) return;

  try {
    await eventFormRef.value.validate();

    if (isEdit.value) {
      // 编辑模式
      const index = events.value.findIndex((e) => e.id === eventForm.id);
      if (index !== -1) {
        events.value[index] = {
          ...eventForm,
          id: eventForm.id,
          title: eventForm.title,
          content: eventForm.content,
          startTime: eventForm.startTime,
          endTime: eventForm.endTime,
          type: eventForm.type,
          status: eventForm.status,
        };

        ElMessage.success("事件已更新");
      }
    } else {
      // 新建模式
      const newId = Math.max(0, ...events.value.map((e) => e.id)) + 1;

      events.value.push({
        id: newId,
        title: eventForm.title,
        content: eventForm.content,
        startTime: eventForm.startTime,
        endTime: eventForm.endTime,
        type: eventForm.type,
        status: eventForm.status,
      });

      ElMessage.success("事件已创建");
    }

    eventDialogVisible.value = false;
  } catch (error) {
    console.error("表单验证失败", error);
  }
};

// 删除事件
const handleDeleteEvent = () => {
  ElMessageBox.confirm("确定要删除这个事件吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      const index = events.value.findIndex((e) => e.id === eventForm.id);
      if (index !== -1) {
        events.value.splice(index, 1);
        ElMessage.success("删除成功");
        eventDialogVisible.value = false;
      }
    })
    .catch(() => {
      // 取消删除
    });
};

// 页面加载时初始化
onMounted(() => {
  // 在实际应用中，这里应该调用API获取事件列表
});
</script>

<style scoped>
.calendar-container {
  padding: 20px 0;
}

.calendar-card,
.events-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date-nav {
  display: flex;
  align-items: center;
}

.current-date {
  margin-left: 15px;
  font-size: 16px;
  font-weight: 500;
}

.calendar-cell {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.day {
  margin: 0;
  text-align: center;
  line-height: 1.5;
}

.event-list {
  flex: 1;
  margin-top: 5px;
  overflow: hidden;
}

.event-item {
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 12px;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}

.event-meeting {
  background-color: #e6f7ff;
  border-left: 2px solid #1890ff;
}

.event-trip {
  background-color: #fff7e6;
  border-left: 2px solid #fa8c16;
}

.event-personal {
  background-color: #f6ffed;
  border-left: 2px solid #52c41a;
}

.event-vacation {
  background-color: #e6fffb;
  border-left: 2px solid #13c2c2;
}

.event-other {
  background-color: #f9f0ff;
  border-left: 2px solid #722ed1;
}

.event-completed {
  opacity: 0.6;
  text-decoration: line-through;
}

.event-card {
  cursor: pointer;
}

.event-card h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.event-desc {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.event-time {
  font-size: 12px;
  color: #909399;
}

/* 自定义日历样式 */
:deep(.el-calendar-table .el-calendar-day) {
  height: 80px;
  padding: 2px;
}

:deep(.el-calendar-table td.is-today) {
  color: #1890ff;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .events-card {
    margin-top: 20px;
  }
}
</style>
