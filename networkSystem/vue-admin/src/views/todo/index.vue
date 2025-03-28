<template>
  <div class="todo-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>待办事项</span>
          <el-button type="primary" @click="handleAdd">新增待办</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索待办事项"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          style="width: 300px"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 待办事项列表 -->
      <el-table v-loading="loading" :data="todoList" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column
          prop="description"
          label="内容"
          min-width="300"
          show-overflow-tooltip
        />
        <el-table-column prop="completed" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.completed ? 'success' : 'warning'">
              {{ row.completed ? "已完成" : "未完成" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.createTime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button
                :type="row.completed ? 'warning' : 'success'"
                :icon="row.completed ? 'Refresh' : 'Check'"
                @click="handleToggleStatus(row)"
              >
                {{ row.completed ? "重启" : "完成" }}
              </el-button>
              <el-button type="primary" icon="Edit" @click="handleEdit(row)">
                编辑
              </el-button>
              <el-button type="danger" icon="Delete" @click="handleDelete(row)">
                删除
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增待办' : '编辑待办'"
      width="500px"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="todoForm"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="todoForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="内容" prop="description">
          <el-input
            v-model="todoForm.description"
            type="textarea"
            rows="4"
            placeholder="请输入内容"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="todoForm.completed"
            :active-text="todoForm.completed ? '已完成' : '未完成'"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { Search } from "@element-plus/icons-vue";
import {
  getTodoList,
  createTodo,
  updateTodo,
  deleteTodo,
  type Todo,
} from "@/api/todo";

// 状态
const loading = ref(false);
const todoList = ref<Todo[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const searchText = ref("");

// 对话框相关
const dialogVisible = ref(false);
const dialogType = ref<"add" | "edit">("add");
const formRef = ref<FormInstance>();
const todoForm = reactive({
  id: undefined as number | undefined,
  title: "",
  description: "",
  completed: false,
  userId: undefined as number | undefined,
  deleted: false,
});

// 表单验证规则
const rules = reactive<FormRules>({
  title: [{ required: true, message: "请输入标题", trigger: "blur" }],
  description: [{ required: true, message: "请输入内容", trigger: "blur" }],
});

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return "";
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

// 获取待办事项列表
const fetchTodoList = async () => {
  loading.value = true;
  try {
    const res = await getTodoList({
      current: currentPage.value,
      size: pageSize.value,
      keyword: searchText.value,
    });
    todoList.value = res.data.records;
    total.value = res.data.total;
  } catch (error) {
    console.error("获取待办事项列表失败:", error);
    ElMessage.error("获取待办事项列表失败");
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  currentPage.value = 1;
  fetchTodoList();
};

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  fetchTodoList();
};

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  fetchTodoList();
};

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields();
  }
  todoForm.id = undefined;
  todoForm.title = "";
  todoForm.description = "";
  todoForm.completed = false;
  todoForm.userId = undefined;
  todoForm.deleted = false;
};

// 新增待办
const handleAdd = () => {
  dialogType.value = "add";
  dialogVisible.value = true;
  resetForm();
};

// 编辑待办
const handleEdit = (row: Todo) => {
  dialogType.value = "edit";
  dialogVisible.value = true;
  // 保存所有原有字段
  Object.assign(todoForm, {
    id: row.id,
    title: row.title,
    description: row.description || "",
    completed: row.completed,
    userId: row.userId,
    deleted: row.deleted,
  });
};

// 切换状态
const handleToggleStatus = async (row: Todo) => {
  try {
    await updateTodo({
      id: row.id!,
      title: row.title,
      description: row.description,
      completed: !row.completed,
      userId: row.userId,
      deleted: row.deleted,
    });
    ElMessage.success("更新成功");
    fetchTodoList();
  } catch (error) {
    console.error("更新失败:", error);
    ElMessage.error("更新失败");
  }
};

// 删除待办
const handleDelete = (row: Todo) => {
  ElMessageBox.confirm("确认删除该待办事项吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(async () => {
    try {
      if (row.id) {
        await deleteTodo(row.id);
        ElMessage.success("删除成功");
        if (todoList.value.length === 1 && currentPage.value > 1) {
          currentPage.value--;
        }
        fetchTodoList();
      }
    } catch (error) {
      console.error("删除失败:", error);
      ElMessage.error("删除失败");
    }
  });
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogType.value === "add") {
          await createTodo({
            title: todoForm.title,
            description: todoForm.description,
            completed: todoForm.completed,
          });
          ElMessage.success("新增成功");
        } else if (todoForm.id) {
          // 更新时发送完整的对象
          await updateTodo({
            id: todoForm.id,
            title: todoForm.title,
            description: todoForm.description,
            completed: todoForm.completed,
            userId: todoForm.userId!,
            deleted: todoForm.deleted ? 1 : 0,
          });
          ElMessage.success("更新成功");
        }
        dialogVisible.value = false;
        fetchTodoList();
      } catch (error: any) {
        console.error("操作失败:", error);
        ElMessage.error(error.message || "操作失败");
      }
    }
  });
};

// 初始化
onMounted(() => {
  fetchTodoList();
});
</script>

<style scoped>
.todo-container {
  min-height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  display: flex;
  margin-bottom: 0;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  margin-top: 20px;
}

:deep(.el-tag) {
  width: 60px;
  text-align: center;
}
</style>
