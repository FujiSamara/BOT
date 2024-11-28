import { createApp } from "vue";
import App from "./App.vue";
import router from "@/router.ts";
import { createPinia } from "pinia";
import components from "@/components/UI";
import VueCookies from "vue-cookies";
import * as config from "@/config";

const app = createApp(App);
const pinia = createPinia();

components.forEach((component) => app.component(component.name!, component));

app
	.use(pinia)
	.use(VueCookies, { expires: config.cookiesExpires })
	.use(router)
	.mount("#app");
