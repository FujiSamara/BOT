import { createRouter, createWebHistory } from "vue-router";
import { useNetworkStore } from "@/store/network";

const routes = [
	{
		path: "/crm",
		children: [
			{
				name: "home",
				path: "",
				component: async () => await import("@/pages/MainPage.vue"),
			},
			{
				name: "login",
				path: "login",
				component: async () => await import("@/pages/AuthPage.vue"),
			},
		],
	},
];

const router = createRouter({
	routes: routes,
	history: createWebHistory(),
});

router.beforeEach(async (to, _) => {
	const networkStore = useNetworkStore();
	const authed = await networkStore.auth();

	if (authed && to.name === "login") {
		return { name: "home" };
	}
	if (!authed && to.name !== "login") {
		return { name: "login" };
	}
});

export default router;
