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
		component: async () => await import("@/pages/MainPage.vue"),
		children: [
			{
				name: "tables",
				path: "tables",
				component: async () =>
					await import("@/pages/panels/TablePanelsPage.vue"),
				children: [
					{
						name: "table-default",
						path: "default",
						component: async () =>
							await import("@/pages/panels/DefaultPanel.vue"),
					},
					{
						name: "table-expenditures",
						path: "expenditures",
						component: async () =>
							await import("@/pages/panels/expenditure/ExpenditurePanel.vue"),
					},
					{
						name: "table-worktimes",
						path: "worktime",
						component: async () =>
							await import("@/pages/panels/worktime/WorktimePanel.vue"),
					},
					{
						name: "table-timesheets",
						path: "timesheet",
						component: async () =>
							await import("@/pages/panels/timesheet/TimesheetPanel.vue"),
					},
					{
						name: "table-bids",
						path: "bid",
						component: async () =>
							await import("@/pages/panels/bid/subpanels/BidPanel.vue"),
					},
					{
						name: "table-readonly-bids",
						path: "readonlybid",
						component: async () =>
							await import("@/pages/panels/bid/subpanels/BidReadOnlyPanel.vue"),
					},
					{
						name: "table-fac-cc-bids",
						path: "facccbid",
						component: async () =>
							await import("@/pages/panels/bid/subpanels/FACAndCCBidPanel.vue"),
					},
					{
						name: "table-fac-cc-history-bids",
						path: "faccchistorybid",
						component: async () =>
							await import(
								"@/pages/panels/bid/subpanels/FACAndCCHistoryBidPanel.vue"
							),
					},
					{
						name: "table-paralegal-bids",
						path: "paralegalbid",
						component: async () =>
							await import(
								"@/pages/panels/bid/subpanels/ParalegalBidPanel.vue"
							),
					},
					{
						name: "table-accountant-card-bids",
						path: "accountantcardbid",
						component: async () =>
							await import(
								"@/pages/panels/bid/subpanels/AccountantCardBidPanel.vue"
							),
					},
					{
						name: "table-my-bids",
						path: "mybid",
						component: async () =>
							await import("@/pages/panels/bid/subpanels/MyBidPanel.vue"),
					},
					{
						name: "table-archive-bids",
						path: "archivebid",
						component: async () =>
							await import("@/pages/panels/bid/subpanels/ArchiveBidPanel.vue"),
					},
				],
			},
		],
	},
	{
		path: "/guest",
		redirect: (to: RouteLocation): RouteLocationRaw => {
			if (to.query.token === undefined || to.query.token_type === undefined) {
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
	{
		name: "login",
		path: "/login",
		component: async () => await import("@/pages/AuthPage.vue"),
	},
	{
		name: "logout",
		path: "/logout",
		component: () => {},
	},
];

const router = createRouter({
	routes: routes,
	history: createWebHistory(),
});

router.beforeEach(async (to, _, next) => {
	const networkStore = useNetworkStore();
	const authed = networkStore.authorized || (await networkStore.auth());

	if (authed) {
		if (to.name === "login") {
			next({ name: "tables" });
		} else {
			if (to.name === "logout") {
				networkStore.logout();
				next({ name: "login" });
			} else {
				next();
			}
		}
	} else {
		if (to.name === "login") {
			next();
		} else {
			next({ name: "login" });
		}
	}
});

export default router;
