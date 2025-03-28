import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import ElementPlus from "element-plus";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import "element-plus/dist/index.css";
import router from "./router";
import pinia from "./stores";

// 创建应用实例
const app = createApp(App);

// 注册Element Plus图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

// 使用插件
app.use(router);
app.use(pinia);
app.use(ElementPlus, { size: "default" });

// 挂载应用
app.mount("#app");
