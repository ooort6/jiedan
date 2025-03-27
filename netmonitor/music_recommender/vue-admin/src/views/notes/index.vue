<template>
  <div class="notes-container">
    <el-row :gutter="20">
      <!-- 左侧分类栏 -->
      <el-col :xs="24" :sm="6" :md="5" :lg="4">
        <el-card class="category-card">
          <template #header>
            <div class="card-header">
              <span>笔记分类</span>
              <el-button
                type="primary"
                text
                @click="$router.push('/categories')"
              >
                管理
              </el-button>
            </div>
          </template>

          <el-menu
            :default-active="activeCategory"
            @select="handleCategorySelect"
          >
            <el-menu-item index="all">
              <el-icon><Document /></el-icon>
              <span>全部笔记</span>
              <template #title>
                <span>全部笔记</span>
                <el-badge :value="noteStats.total" class="item" type="info" />
              </template>
            </el-menu-item>

            <el-menu-item index="favorite">
              <el-icon><Star /></el-icon>
              <span>收藏笔记</span>
              <template #title>
                <span>收藏笔记</span>
                <el-badge
                  :value="noteStats.favorite"
                  class="item"
                  type="warning"
                />
              </template>
            </el-menu-item>

            <el-sub-menu index="categories">
              <template #title>
                <el-icon><Folder /></el-icon>
                <span>按分类</span>
              </template>

              <el-menu-item
                v-for="category in categories"
                :key="category.id"
                :index="'category-' + category.id"
              >
                {{ category.name }}
                <el-badge :value="category.count" class="item" />
              </el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-card>
      </el-col>

      <!-- 右侧笔记列表 -->
      <el-col :xs="24" :sm="18" :md="19" :lg="20">
        <el-card class="notes-list-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <span>{{ currentCategoryName }}</span>
                <span class="note-count">共 {{ noteList.length }} 条笔记</span>
              </div>

              <div class="header-right">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索笔记"
                  :prefix-icon="Search"
                  clearable
                  @clear="handleSearch"
                  @input="handleSearch"
                  style="width: 250px; margin-right: 15px"
                />

                <el-button type="primary" @click="handleCreateNote">
                  <el-icon><Plus /></el-icon> 新建笔记
                </el-button>
              </div>
            </div>
          </template>

          <!-- 笔记列表 -->
          <el-empty v-if="filteredNotes.length === 0" description="暂无笔记" />

          <el-row :gutter="20" v-else>
            <el-col
              v-for="note in filteredNotes"
              :key="note.id"
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
              :xl="4"
            >
              <el-card class="note-card" shadow="hover">
                <template #header>
                  <div class="note-header">
                    <el-tooltip
                      :content="note.title"
                      placement="top"
                      :show-after="1000"
                    >
                      <h3 class="note-title">{{ note.title }}</h3>
                    </el-tooltip>

                    <div class="note-actions">
                      <el-dropdown
                        trigger="click"
                        @command="(cmd) => handleCommand(cmd, note)"
                      >
                        <el-button type="text">
                          <el-icon><More /></el-icon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item command="edit"
                              >编辑</el-dropdown-item
                            >
                            <el-dropdown-item
                              command="favorite"
                              :divided="true"
                            >
                              {{ note.favorite ? "取消收藏" : "收藏" }}
                            </el-dropdown-item>
                            <el-dropdown-item command="delete" :divided="true"
                              >删除</el-dropdown-item
                            >
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                  </div>
                </template>

                <div class="note-content">
                  {{ note.content || "无内容" }}
                </div>

                <div class="note-footer">
                  <el-tag size="small">{{
                    getCategoryName(note.category)
                  }}</el-tag>
                  <span class="note-time">{{
                    formatDate(note.updatedAt)
                  }}</span>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新建/编辑笔记对话框 -->
    <el-dialog
      v-model="noteDialogVisible"
      :title="isEdit ? '编辑笔记' : '新建笔记'"
      width="600px"
      destroy-on-close
    >
      <el-form
        :model="noteForm"
        label-width="80px"
        ref="noteFormRef"
        :rules="noteRules"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="noteForm.title" placeholder="请输入标题" />
        </el-form-item>

        <el-form-item label="分类" prop="category">
          <el-select v-model="noteForm.category" placeholder="请选择分类">
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="内容" prop="content">
          <el-input
            v-model="noteForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入笔记内容"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="noteForm.favorite">收藏</el-checkbox>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveNote">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from "vue";
import {
  Document,
  Star,
  Folder,
  Search,
  More,
  Plus,
} from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox, FormInstance, FormRules } from "element-plus";

// 数据类型定义
interface Category {
  id: number;
  name: string;
  count: number;
}

interface Note {
  id: number;
  title: string;
  content: string;
  category: number;
  favorite: boolean;
  createdAt: string;
  updatedAt: string;
}

// 分类列表
const categories = ref<Category[]>([
  { id: 1, name: "工作", count: 3 },
  { id: 2, name: "学习", count: 2 },
  { id: 3, name: "生活", count: 1 },
]);

// 笔记统计
const noteStats = reactive({
  total: 6,
  favorite: 2,
});

// 笔记列表
const noteList = ref<Note[]>([
  {
    id: 1,
    title: "Vue3学习笔记",
    content: "Vue3的组合式API使用方法总结，包括ref、reactive、computed等...",
    category: 2,
    favorite: true,
    createdAt: "2025-03-20 14:30",
    updatedAt: "2025-03-25 10:15",
  },
  {
    id: 2,
    title: "项目会议纪要",
    content:
      "今天讨论了项目进度和下一阶段的工作计划，主要包括功能优化和性能提升两个方面...",
    category: 1,
    favorite: false,
    createdAt: "2025-03-24 09:30",
    updatedAt: "2025-03-24 09:30",
  },
  {
    id: 3,
    title: "周末计划",
    content: "1. 看电影《奥本海默》\n2. 整理房间\n3. 学习React",
    category: 3,
    favorite: true,
    createdAt: "2025-03-22 18:00",
    updatedAt: "2025-03-22 18:00",
  },
  {
    id: 4,
    title: "TypeScript学习笔记",
    content:
      "TypeScript 是 JavaScript 的超集，提供了类型系统和对 ES6+ 的支持...",
    category: 2,
    favorite: false,
    createdAt: "2025-03-21 11:20",
    updatedAt: "2025-03-21 11:20",
  },
  {
    id: 5,
    title: "产品需求分析",
    content:
      "根据用户反馈，我们需要优先实现以下功能：\n1. 暗黑模式\n2. 数据导出\n3. 移动端适配",
    category: 1,
    favorite: false,
    createdAt: "2025-03-23 15:40",
    updatedAt: "2025-03-23 15:40",
  },
  {
    id: 6,
    title: "代码评审记录",
    content:
      "今天评审了登录模块的代码，发现了以下问题：\n1. 异常处理不完善\n2. 缺少单元测试",
    category: 1,
    favorite: false,
    createdAt: "2025-03-25 13:10",
    updatedAt: "2025-03-25 13:10",
  },
]);

// 当前选中的分类
const activeCategory = ref("all");
const currentCategoryName = computed(() => {
  if (activeCategory.value === "all") return "全部笔记";
  if (activeCategory.value === "favorite") return "收藏笔记";

  if (activeCategory.value.startsWith("category-")) {
    const categoryId = parseInt(activeCategory.value.split("-")[1]);
    const category = categories.value.find((c) => c.id === categoryId);
    return category ? category.name : "未知分类";
  }

  return "笔记";
});

// 筛选笔记
const searchKeyword = ref("");
const filteredNotes = computed(() => {
  let result = [...noteList.value];

  // 按分类筛选
  if (activeCategory.value === "favorite") {
    result = result.filter((note) => note.favorite);
  } else if (activeCategory.value.startsWith("category-")) {
    const categoryId = parseInt(activeCategory.value.split("-")[1]);
    result = result.filter((note) => note.category === categoryId);
  }

  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    result = result.filter(
      (note) =>
        note.title.toLowerCase().includes(keyword) ||
        note.content.toLowerCase().includes(keyword)
    );
  }

  // 按更新时间排序
  return result.sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );
});

// 分类选择
const handleCategorySelect = (index: string) => {
  activeCategory.value = index;
};

// 搜索
const handleSearch = () => {
  // 在这里不需要额外操作，因为已经通过计算属性处理了搜索结果
};

// 获取分类名称
const getCategoryName = (categoryId: number) => {
  const category = categories.value.find((c) => c.id === categoryId);
  return category ? category.name : "未分类";
};

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  const now = new Date();

  // 如果是今天，只显示时间
  if (date.toDateString() === now.toDateString()) {
    return `今天 ${date.getHours().toString().padStart(2, "0")}:${date
      .getMinutes()
      .toString()
      .padStart(2, "0")}`;
  }

  // 否则显示日期
  return `${date.getMonth() + 1}月${date.getDate()}日`;
};

// 笔记对话框
const noteDialogVisible = ref(false);
const isEdit = ref(false);
const noteFormRef = ref<FormInstance>();
const noteForm = reactive({
  id: 0,
  title: "",
  content: "",
  category: 1,
  favorite: false,
});

// 表单验证规则
const noteRules: FormRules = {
  title: [
    { required: true, message: "请输入笔记标题", trigger: "blur" },
    { max: 50, message: "标题长度不能超过50个字符", trigger: "blur" },
  ],
  category: [{ required: true, message: "请选择分类", trigger: "change" }],
};

// 新建笔记
const handleCreateNote = () => {
  isEdit.value = false;
  noteForm.id = 0;
  noteForm.title = "";
  noteForm.content = "";
  noteForm.category = 1;
  noteForm.favorite = false;
  noteDialogVisible.value = true;
};

// 编辑笔记
const handleEditNote = (note: Note) => {
  isEdit.value = true;
  noteForm.id = note.id;
  noteForm.title = note.title;
  noteForm.content = note.content;
  noteForm.category = note.category;
  noteForm.favorite = note.favorite;
  noteDialogVisible.value = true;
};

// 收藏/取消收藏笔记
const handleToggleFavorite = (note: Note) => {
  note.favorite = !note.favorite;
  ElMessage.success(note.favorite ? "已收藏" : "已取消收藏");

  // 更新统计
  noteStats.favorite = noteList.value.filter((n) => n.favorite).length;
};

// 删除笔记
const handleDeleteNote = (note: Note) => {
  ElMessageBox.confirm("确定要删除这条笔记吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      // 模拟删除
      const index = noteList.value.findIndex((n) => n.id === note.id);
      if (index !== -1) {
        noteList.value.splice(index, 1);

        // 更新统计
        noteStats.total = noteList.value.length;
        noteStats.favorite = noteList.value.filter((n) => n.favorite).length;

        // 更新分类计数
        const category = categories.value.find((c) => c.id === note.category);
        if (category) {
          category.count--;
        }

        ElMessage.success("删除成功");
      }
    })
    .catch(() => {
      // 取消删除
    });
};

// 保存笔记
const handleSaveNote = async () => {
  if (!noteFormRef.value) return;

  try {
    await noteFormRef.value.validate();

    if (isEdit.value) {
      // 编辑模式
      const index = noteList.value.findIndex((n) => n.id === noteForm.id);
      if (index !== -1) {
        // 如果分类改变，更新分类计数
        if (noteList.value[index].category !== noteForm.category) {
          // 原分类计数减1
          const oldCategory = categories.value.find(
            (c) => c.id === noteList.value[index].category
          );
          if (oldCategory) {
            oldCategory.count--;
          }

          // 新分类计数加1
          const newCategory = categories.value.find(
            (c) => c.id === noteForm.category
          );
          if (newCategory) {
            newCategory.count++;
          }
        }

        // 如果收藏状态改变，更新收藏计数
        if (noteList.value[index].favorite !== noteForm.favorite) {
          noteStats.favorite += noteForm.favorite ? 1 : -1;
        }

        // 更新笔记
        noteList.value[index] = {
          ...noteList.value[index],
          title: noteForm.title,
          content: noteForm.content,
          category: noteForm.category,
          favorite: noteForm.favorite,
          updatedAt: new Date().toISOString().replace("T", " ").substr(0, 16),
        };

        ElMessage.success("笔记已更新");
      }
    } else {
      // 新建模式
      const newId = Math.max(0, ...noteList.value.map((n) => n.id)) + 1;
      const now = new Date().toISOString().replace("T", " ").substr(0, 16);

      // 添加新笔记
      noteList.value.push({
        id: newId,
        title: noteForm.title,
        content: noteForm.content,
        category: noteForm.category,
        favorite: noteForm.favorite,
        createdAt: now,
        updatedAt: now,
      });

      // 更新统计
      noteStats.total++;
      if (noteForm.favorite) {
        noteStats.favorite++;
      }

      // 更新分类计数
      const category = categories.value.find((c) => c.id === noteForm.category);
      if (category) {
        category.count++;
      }

      ElMessage.success("笔记已创建");
    }

    noteDialogVisible.value = false;
  } catch (error) {
    console.error("表单验证失败", error);
  }
};

// 处理更多菜单命令
const handleCommand = (command: string, note: Note) => {
  switch (command) {
    case "edit":
      handleEditNote(note);
      break;
    case "favorite":
      handleToggleFavorite(note);
      break;
    case "delete":
      handleDeleteNote(note);
      break;
  }
};

// 页面加载时初始化
onMounted(() => {
  // 在实际应用中，这里应该调用API获取分类和笔记列表
});
</script>

<style scoped>
.notes-container {
  padding: 20px 0;
}

.category-card,
.notes-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.note-count {
  font-size: 14px;
  color: #909399;
  margin-left: 10px;
}

.header-right {
  display: flex;
  align-items: center;
}

.note-card {
  margin-bottom: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.note-title {
  margin: 0;
  font-size: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.note-content {
  margin: 10px 0;
  color: #606266;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  flex: 1;
}

.note-footer {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.note-time {
  color: #909399;
}

/* 菜单样式调整 */
:deep(.el-menu-item) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-badge__content) {
  font-size: 10px;
  padding: 0 4px;
  height: 16px;
  line-height: 16px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .category-card {
    margin-bottom: 15px;
  }

  .note-card {
    margin-bottom: 15px;
  }
}
</style>
