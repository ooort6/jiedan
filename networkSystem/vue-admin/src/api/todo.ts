import request from "@/utils/request";

export interface Todo {
  id?: number;
  title: string;
  description: string | null;
  completed: boolean;
  deleted: number;
  userId: number;
  createTime?: string;
  updateTime?: string;
}

interface TodoQuery {
  current: number;
  size: number;
  keyword?: string;
}

interface TodoResponse {
  data: {
    records: Todo[];
    total: number;
    size: number;
    current: number;
  };
}

// 获取待办事项列表
export function getTodoList(params: TodoQuery): Promise<TodoResponse> {
  return request({
    url: "/api/todos",
    method: "get",
    params,
  });
}

// 创建待办事项
export function createTodo(data: Partial<Todo>) {
  return request({
    url: "/api/todos",
    method: "post",
    data,
  });
}

// 更新待办事项
export function updateTodo(data: Todo) {
  return request({
    url: `/api/todos/${data.id}`,
    method: "put",
    data,
  });
}

// 删除待办事项
export function deleteTodo(id: number) {
  return request({
    url: `/api/todos/${id}`,
    method: "delete",
  });
}
