<template>
  <div class="categories-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <el-button type="primary" @click="handleCreateCategory">
            <el-icon><Plus /></el-icon> 添加分类
          </el-button>
        </div>
      </template>

      <div class="filter-container">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索分类名称"
          clearable
          class="filter-item"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="filterStatus"
          placeholder="状态筛选"
          clearable
          class="filter-item"
          @change="handleSearch"
        >
          <el-option label="启用" value="active" />
          <el-option label="禁用" value="inactive" />
        </el-select>

        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>

      <el-table
        v-loading="tableLoading"
        :data="filteredCategories"
        border
        style="width: 100%"
        row-key="id"
      >
        <el-table-column label="ID" prop="id" width="80" />

        <el-table-column label="名称" min-width="150">
          <template #default="{ row }">
            <div class="category-name">
              <el-tag :type="getCategoryType(row)" class="category-tag">
                {{ row.type }}
              </el-tag>
              {{ row.name }}
            </div>
          </template>
        </el-table-column>

        <el-table-column
          label="描述"
          prop="description"
          min-width="200"
          :show-overflow-tooltip="true"
        />

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === "active" ? "启用" : "禁用" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEditCategory(row)">
              编辑
            </el-button>
            <el-button
              type="success"
              link
              v-if="row.status === 'inactive'"
              @click="handleToggleStatus(row)"
            >
              启用
            </el-button>
            <el-button type="info" link v-else @click="handleToggleStatus(row)">
              禁用
            </el-button>
            <el-button type="danger" link @click="handleDeleteCategory(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredTotal"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 分类表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑分类' : '新增分类'"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="categoryFormRef"
        :model="categoryForm"
        :rules="categoryRules"
        label-width="100px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>

        <el-form-item label="分类类型" prop="type">
          <el-select v-model="categoryForm.type" placeholder="请选择分类类型">
            <el-option label="笔记分类" value="note" />
            <el-option label="日程分类" value="calendar" />
            <el-option label="系统分类" value="system" />
            <el-option label="其他分类" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="分类描述" prop="description">
          <el-input
            v-model="categoryForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          />
        </el-form-item>

        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="categoryForm.sort" :min="0" :max="1000" />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="categoryForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitCategoryForm"
          :loading="submitLoading"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { Plus, Search } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox, FormInstance, FormRules } from "element-plus";
import dayjs from "dayjs";

// 类型定义
interface Category {
  id: number;
  name: string;
  type: "note" | "calendar" | "system" | "other";
  description: string;
  sort: number;
  status: "active" | "inactive";
  createdAt: string;
  updatedAt: string;
}

// 表格数据
const tableLoading = ref(false);
const categories = ref<Category[]>([
  {
    id: 1,
    name: "工作笔记",
    type: "note",
    description: "用于记录工作相关的笔记、会议记录等",
    sort: 0,
    status: "active",
    createdAt: "2025-02-15T08:00:00",
    updatedAt: "2025-02-15T08:00:00",
  },
  {
    id: 2,
    name: "学习笔记",
    type: "note",
    description: "用于记录学习过程中的知识点、心得体会等",
    sort: 1,
    status: "active",
    createdAt: "2025-02-16T10:30:00",
    updatedAt: "2025-02-16T10:30:00",
  },
  {
    id: 3,
    name: "项目会议",
    type: "calendar",
    description: "项目相关的会议安排",
    sort: 0,
    status: "active",
    createdAt: "2025-02-17T14:20:00",
    updatedAt: "2025-02-17T14:20:00",
  },
  {
    id: 4,
    name: "休假计划",
    type: "calendar",
    description: "个人休假、团队出游等计划",
    sort: 1,
    status: "active",
    createdAt: "2025-02-18T09:15:00",
    updatedAt: "2025-02-18T09:15:00",
  },
  {
    id: 5,
    name: "系统默认",
    type: "system",
    description: "系统默认分类，不可删除",
    sort: 0,
    status: "active",
    createdAt: "2025-02-10T00:00:00",
    updatedAt: "2025-02-10T00:00:00",
  },
  {
    id: 6,
    name: "归档分类",
    type: "other",
    description: "用于存放已归档的内容",
    sort: 10,
    status: "inactive",
    createdAt: "2025-02-20T16:40:00",
    updatedAt: "2025-02-20T16:40:00",
  },
]);

// 搜索和筛选
const searchKeyword = ref("");
const filterStatus = ref("");

const filteredCategories = computed(() => {
  let result = [...categories.value];

  // 关键字搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    result = result.filter(
      (item) =>
        item.name.toLowerCase().includes(keyword) ||
        item.description.toLowerCase().includes(keyword)
    );
  }

  // 状态筛选
  if (filterStatus.value) {
    result = result.filter((item) => item.status === filterStatus.value);
  }

  // 根据排序字段排序
  result.sort((a, b) => a.sort - b.sort);

  return result.slice(
    (currentPage.value - 1) * pageSize.value,
    currentPage.value * pageSize.value
  );
});

const filteredTotal = computed(() => {
  let result = [...categories.value];

  // 关键字搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    result = result.filter(
      (item) =>
        item.name.toLowerCase().includes(keyword) ||
        item.description.toLowerCase().includes(keyword)
    );
  }

  // 状态筛选
  if (filterStatus.value) {
    result = result.filter((item) => item.status === filterStatus.value);
  }

  return result.length;
});

// 分页
const currentPage = ref(1);
const pageSize = ref(10);

const handleSizeChange = (val: number) => {
  pageSize.value = val;
  currentPage.value = 1;
};

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
};

// 搜索和重置
const handleSearch = () => {
  currentPage.value = 1;
};

const resetFilter = () => {
  searchKeyword.value = "";
  filterStatus.value = "";
  currentPage.value = 1;
};

// 格式化日期
const formatDate = (dateStr: string) => {
  return dayjs(dateStr).format("YYYY-MM-DD HH:mm");
};

// 获取分类类型样式
const getCategoryType = (category: Category) => {
  switch (category.type) {
    case "note":
      return "success";
    case "calendar":
      return "primary";
    case "system":
      return "danger";
    case "other":
      return "info";
    default:
      return "";
  }
};

// 分类表单
const dialogVisible = ref(false);
const isEdit = ref(false);
const submitLoading = ref(false);
const categoryFormRef = ref<FormInstance>();

const categoryForm = reactive({
  id: 0,
  name: "",
  type: "note" as const,
  description: "",
  sort: 0,
  status: "active" as const,
});

const categoryRules: FormRules = {
  name: [
    { required: true, message: "请输入分类名称", trigger: "blur" },
    { min: 2, max: 20, message: "长度应为2-20个字符", trigger: "blur" },
  ],
  type: [{ required: true, message: "请选择分类类型", trigger: "change" }],
  description: [
    { max: 200, message: "描述不能超过200个字符", trigger: "blur" },
  ],
};

// 添加分类
const handleCreateCategory = () => {
  isEdit.value = false;
  categoryForm.id = 0;
  categoryForm.name = "";
  categoryForm.type = "note";
  categoryForm.description = "";
  categoryForm.sort = 0;
  categoryForm.status = "active";
  dialogVisible.value = true;
};

// 编辑分类
const handleEditCategory = (row: Category) => {
  isEdit.value = true;
  categoryForm.id = row.id;
  categoryForm.name = row.name;
  categoryForm.type = row.type;
  categoryForm.description = row.description;
  categoryForm.sort = row.sort;
  categoryForm.status = row.status;
  dialogVisible.value = true;
};

// 切换状态
const handleToggleStatus = (row: Category) => {
  const newStatus = row.status === "active" ? "inactive" : "active";
  ElMessageBox.confirm(
    `确定要${newStatus === "active" ? "启用" : "禁用"}该分类吗？`,
    "提示",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    }
  )
    .then(() => {
      // 在真实环境中，这里应该调用API
      const index = categories.value.findIndex((item) => item.id === row.id);
      if (index !== -1) {
        categories.value[index].status = newStatus;
        ElMessage.success(`已${newStatus === "active" ? "启用" : "禁用"}`);
      }
    })
    .catch(() => {
      // 取消操作
    });
};

// 删除分类
const handleDeleteCategory = (row: Category) => {
  if (row.type === "system") {
    ElMessage.warning("系统分类不可删除");
    return;
  }

  ElMessageBox.confirm("确定要删除该分类吗？删除后无法恢复！", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(() => {
      // 在真实环境中，这里应该调用API
      const index = categories.value.findIndex((item) => item.id === row.id);
      if (index !== -1) {
        categories.value.splice(index, 1);
        ElMessage.success("删除成功");
      }
    })
    .catch(() => {
      // 取消操作
    });
};

// 提交表单
const submitCategoryForm = async () => {
  if (!categoryFormRef.value) return;

  try {
    await categoryFormRef.value.validate();
    submitLoading.value = true;

    // 模拟API请求
    setTimeout(() => {
      if (isEdit.value) {
        // 编辑模式
        const index = categories.value.findIndex(
          (item) => item.id === categoryForm.id
        );
        if (index !== -1) {
          categories.value[index] = {
            ...categories.value[index],
            name: categoryForm.name,
            type: categoryForm.type,
            description: categoryForm.description,
            sort: categoryForm.sort,
            status: categoryForm.status,
            updatedAt: dayjs().format("YYYY-MM-DDTHH:mm:ss"),
          };
          ElMessage.success("更新成功");
        }
      } else {
        // 新增模式
        const newId =
          Math.max(0, ...categories.value.map((item) => item.id)) + 1;
        const now = dayjs().format("YYYY-MM-DDTHH:mm:ss");

        categories.value.push({
          id: newId,
          name: categoryForm.name,
          type: categoryForm.type,
          description: categoryForm.description,
          sort: categoryForm.sort,
          status: categoryForm.status,
          createdAt: now,
          updatedAt: now,
        });

        ElMessage.success("添加成功");
      }

      submitLoading.value = false;
      dialogVisible.value = false;
    }, 500);
  } catch (error) {
    console.error("表单验证失败", error);
  }
};

onMounted(() => {
  // 在实际应用中，这里应该调用API获取分类数据
});
</script>

<style scoped>
.categories-container {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-container {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-item {
  width: 220px;
}

.category-name {
  display: flex;
  align-items: center;
}

.category-tag {
  margin-right: 8px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .filter-item {
    width: 100%;
  }
}
</style>
