import { createApp } from "vue"
import Antd from "ant-design-vue";
import App from "./App.vue"
import "ant-design-vue/dist/reset.css";

const app = createApp(App)

app.config.globalProperties.backendUrl = "http://10.0.120.100/api/v1/backend/";
app.use(Antd).mount('#app')
