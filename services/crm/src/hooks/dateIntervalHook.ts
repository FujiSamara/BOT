import { Table } from "@/components/table";
import { BaseSchema, DateSchema } from "@/types";
import { useRoute, useRouter } from "vue-router";

export const useDateInterval = (
	table: Table<BaseSchema>,
	column: string,
): {
	submit: (from: Date, to: Date) => void;
	unset: () => void;
} => {
	const router = useRouter();
	const route = useRoute();

	const submit = (from: Date, to: Date) => {
		const dateQuery: DateSchema = {
			column: column,
			start: from,
			end: to,
		};

		table.byDate.value = dateQuery;
	};

	const unset = () => {
		table.byDate.value = undefined;
	};

	return {
		submit,
		unset,
	};
};
