import {
	createRouter,
	createWebHistory,
	RouteLocation,
	RouteLocationRaw,
} from "vue-router";
import { useNetworkStore } from "@/store/network";

const routes = [
	{
		path: "/crm",
		children: [
			{
				name: "tables",
				path: "/tables",
				component: async () => await import("@/pages/TablePanelsPage.vue"),
				children: [
					{
						path: "expenditures",
						component: async () =>
							await import("@/pages/panels/ExpenditurePanel.vue"),
					},
				],
			},
			{
				name: "default",
				path: "",
				redirect: "/tables",
			},
			{
				name: "login",
				path: "login",
				component: async () => await import("@/pages/AuthPage.vue"),
			},
			{
				path: "guest",
				redirect: (to: RouteLocation): RouteLocationRaw => {
					if (
						to.query.token === undefined ||
						to.query.token_type === undefined
					) {
						return { name: "login" };
					}

					const network = useNetworkStore();
					network.setCredentials(
						to.query.token as string,
						to.query.token_type as string,
					);

					to.query = {};

					return { name: "home" };
				},
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
		return { name: "tables" };
	}
	if (!authed && to.name !== "login") {
		return { name: "login" };
	}
});

export default router;
