import { ref, Ref } from "vue";
import { Table } from "@/components/table";
import { BaseSchema, RouteData } from "@/types";

export interface DateIntervalModelOut {
	submit: (from: Date, to: Date) => void;
	unset: () => void;
	from: Date | undefined;
	to: Date | undefined;
	exist: Ref<boolean>;
}

export const useDateInterval = async (
	table: Table<BaseSchema>,
	column: string,
	routeData: RouteData,
): Promise<DateIntervalModelOut> => {
	const exist = ref(false);
	const route = routeData.route;
	const router = routeData.router;

	const submit = async (from: Date, to: Date, silent: boolean = false) => {
		await change({ from, to }, silent);
		exist.value = true;
	};

	const unset = async (silent: boolean = false) => {
		await change(undefined, silent);
		exist.value = false;
	};

	const change = async (
		inteval?: { from: Date; to: Date },
		silent: boolean = false,
	) => {
		let dateQuery = undefined;
		if (inteval) {
			dateQuery = {
				column: column,
				start: inteval.from,
				end: inteval.to,
			};
		}

		table.byDate.value = dateQuery;

		if (silent) return;

		const query = { ...route.query };

		if (!inteval) {
			if ("from" in query) {
				delete query["from"];
				delete query["to"];
			}
			await router.replace({ query });
			return;
		}

		query["from"] = inteval.from.getTime().toString();
		query["to"] = inteval.to.getTime().toString();

		await router.replace({ query });
	};

	let from;
	let to;

	if ("from" in route.query) {
		from = new Date(parseInt(route.query["from"] as string));
		to = new Date(parseInt(route.query["to"] as string));
		await submit(from, to, true);
	}

	return {
		submit,
		unset,
		from,
		to,
		exist,
	};
};
