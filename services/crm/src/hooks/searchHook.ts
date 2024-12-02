import { Table } from "@/components/table";
import { BaseSchema, SearchSchema } from "@/types";
import { Ref, ref, watch } from "vue";

interface SearchModelIn {
	schemas: {
		pattern: string; // Pattern in format: parent.child.grandson...
		groups: number[];
	}[];
	style?: string;
	placeholder?: string;
}

interface SearchModelOut {
	onInput: (value: string) => void;
	style?: string;
	placeholder?: string;
	error: Ref<string | undefined>;
}

export const useSearch = (
	table: Table<BaseSchema>,
	...modelsIn: SearchModelIn[]
): SearchModelOut[] => {
	const values = modelsIn.map((_) => "");
	const listeners = modelsIn.map((_, index) => {
		const onModelChanged = (value: string) => {
			values[index] = value;
			onInput();
		};
		return onModelChanged;
	});
	const errors: Ref<string | undefined>[] = modelsIn.map((_) => ref(undefined));

	const onInput = () => {
		const result: SearchSchema[] = [];

		for (let index = 0; index < modelsIn.length; index++) {
			const modelIn = modelsIn[index];
			const term = values[index] !== undefined ? values[index] : "";

			for (const schema of modelIn.schemas) {
				const fields = schema.pattern.split(".");

				if (term.length > 3) {
					const searchSchema = applyPattern(fields, term);

					searchSchema.groups = schema.groups;

					result.push(searchSchema);
				}
			}
		}

		table.searchQuery.value = result;
	};

	watch(table.rows, () => {
		if (table.isLoading.value) {
			return;
		}

		for (let index = 0; index < values.length; index++) {
			const value = values[index];
			const error = errors[index];

			if (table.rows.value.length === 0 && value) {
				error.value = "Соответствия не найдены";
			} else {
				error.value = undefined;
			}
		}
	});

	const result: SearchModelOut[] = [];
	for (let index = 0; index < values.length; index++) {
		result.push({
			onInput: listeners[index],
			error: errors[index],
			placeholder: modelsIn[index].placeholder,
			style: modelsIn[index].style,
		});
	}

	return result;
};

const applyPattern = (fields: string[], term: string): SearchSchema => {
	const deps = [];
	let completedTerm = term;

	if (fields.length > 1) {
		completedTerm = "";
		deps.push(applyPattern(fields.slice(1), term));
	}

	const result: SearchSchema = {
		column: fields[0],
		term: completedTerm,
		dependencies: deps,
	};

	return result;
};
