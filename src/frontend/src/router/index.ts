import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/store/auth";

const pageLoader = (pageImport: any) => {
	return async () => {
		const authStore = useAuthStore();
		const isAuthed = await authStore.auth();
		if (isAuthed) return await pageImport;
		else return await import("@/pages/AuthPage.vue");
	};
};

const routes = [
	{
		path: "/",
		component: pageLoader(import("@/pages/MainPage.vue")),
	},
];

const router = createRouter({
	routes,
	history: createWebHistory(),
});
export default router;
