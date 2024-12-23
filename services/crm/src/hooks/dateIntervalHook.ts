import { Table } from "@/components/table";
import { BaseSchema, DateSchema } from "@/types";

export const useDateInterval = (
	table: Table<BaseSchema>,
	column: string,
): {
	submit: (from: Date, to: Date) => void;
} => {
	const submit = (from: Date, to: Date) => {
		const dateQuery: DateSchema = {
			column: column,
			start: from,
			end: to,
		};

		table.byDate.value = dateQuery;
	};

	return {
		submit,
	};
};
