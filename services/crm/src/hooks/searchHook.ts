import { Table } from "@/components/table";
import { BaseSchema, SearchSchema } from "@/types";

interface SearchModelIn {
	schemas: {
		pattern: string; // Pattern in format: parent.child.grandson...
		groups: number[];
	}[];
}

export const useSearch = (
	table: Table<BaseSchema>,
	...modelsIn: SearchModelIn[]
): { onInput: (value: string) => void }[] => {
	const values = new Array<string>(modelsIn.length);
	const listeners = modelsIn.map((_, index) => {
		const onModelChanged = (value: string) => {
			values[index] = value;
			onInput();
		};
		return { onInput: onModelChanged };
	});

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

	return listeners;
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
