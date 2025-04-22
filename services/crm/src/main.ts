import { createApp } from "vue";
import App from "./App.vue";
import router from "@/router.ts";
import { createPinia } from "pinia";
import components from "@/components/UI";
import VueCookies from "vue-cookies";
import Vue3Toastify, { type ToastContainerOptions } from "vue3-toastify";
import "vue3-toastify/dist/index.css";
import * as config from "@/config";
import "@/assets/scss/main.scss";
import "gridjs/dist/theme/mermaid.css";

const app = createApp(App);
const pinia = createPinia();

components.forEach((component) => app.component(component.name!, component));

app
	.use(pinia)
	.use(VueCookies, { expires: config.cookiesExpires })
	.use(router)
	.use(Vue3Toastify, {
		autoClose: 3000,
	} as ToastContainerOptions)
	.mount("#app");
