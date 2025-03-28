# Vue Admin

基于 Vue 3 + TypeScript + Element Plus 构建的现代化管理系统前端。

## 项目特点

- 🚀 使用 Vue 3.0 组合式 API
- 🔥 基于 TypeScript 提供类型支持
- 💎 集成 Element Plus 组件库
- 📱 响应式布局，支持移动端
- 🔒 JWT 认证，路由权限控制
- 📊 丰富的页面组件：登录、控制台、个人信息、笔记管理、日程安排、分类管理

## 技术栈

- **前端框架**：Vue 3.x
- **构建工具**：Vite
- **UI 组件库**：Element Plus
- **状态管理**：Pinia
- **路由管理**：Vue Router
- **HTTP 请求**：Axios
- **代码规范**：ESLint + Prettier

## 项目结构

```
vue-admin/
├── public/                  # 静态资源
│   ├── api/                 # API 接口封装
│   ├── assets/              # 项目资源文件
│   ├── components/          # 公共组件
│   ├── layouts/             # 布局组件
│   ├── router/              # 路由配置
│   ├── stores/              # Pinia 状态管理
│   ├── utils/               # 工具函数
│   ├── views/               # 页面组件
│   ├── App.vue              # 根组件
│   └── main.ts              # 入口文件
├── .gitignore               # Git 忽略文件
├── index.html               # HTML 模板
├── package.json             # 项目依赖
├── tsconfig.json            # TypeScript 配置
└── vite.config.ts           # Vite 配置
```

## 后端接口

本项目使用位于 `backend` 目录的 Spring Boot 后端服务，主要包括：

- 用户认证 (JWT)
- 笔记管理
- 日程管理
- 分类管理

## 安装与运行

```bash
# 安装依赖
npm install

# 开发环境运行
npm run dev

# 生产环境构建
npm run build
```

## 注意事项

1. 确保后端服务已正确启动（默认端口：8080）
2. 开发环境默认端口为 5173
3. 接口代理配置位于 `vite.config.ts` 文件中

## 截图展示

- 登录页面：简洁的登录界面，支持账号密码验证
- 控制台：数据概览，包含统计数据和最近内容
- 个人信息：用户信息展示与编辑
- 笔记管理：支持创建、编辑、删除笔记
- 日程安排：日历视图，管理日程和事件
- 分类管理：对笔记分类进行管理

## 许可证

[MIT](LICENSE)
