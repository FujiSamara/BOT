import { Table } from "@/components/table";
import { BaseSchema, SearchSchema } from "@/types";
import { Ref, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

interface SearchModelIn {
	schemas: {
		pattern: string; // Pattern in format: parent.child.grandson...
		groups: number[];
	}[];
	name: string;
	style?: string;
	placeholder?: string;
}

interface SearchModelOut {
	onInput: (value: string) => void;
	style?: string;
	placeholder?: string;
	error: Ref<string | undefined>;
	value: Ref<string>;
}

export const useSearch = (
	table: Table<BaseSchema>,
	...modelsIn: SearchModelIn[]
): SearchModelOut[] => {
	const values = modelsIn.map((_) => "");
	const errors: Ref<string | undefined>[] = modelsIn.map((_) => ref(undefined));
	const modelsOut: SearchModelOut[] = [];
	const listeners = modelsIn.map((_, index) => {
		const onModelChanged = (value: string) => {
			console.log(value);
			modelsOut[index].value.value = value;
			values[index] = value;
			onInput();
		};
		return onModelChanged;
	});

	const router = useRouter();
	const route = useRoute();

	// Fills values from routes
	for (let index = 0; index < modelsIn.length; index++) {
		const name = `${modelsIn[index].name}Search`;

		if (name in route.query) {
			values[index] = route.query[name] as string;
		}
	}

	const onInput = () => {
		const result: SearchSchema[] = [];

		const query = { ...route.query };

		for (let index = 0; index < modelsIn.length; index++) {
			const modelIn = modelsIn[index];
			const term = values[index] !== undefined ? values[index] : "";

			if (term !== "") {
				query[`${modelIn.name}Search`] = term;
			} else {
				delete query[`${modelIn.name}Search`];
			}

			for (const schema of modelIn.schemas) {
				const fields = schema.pattern.split(".");

				if (term.length > 3) {
					const searchSchema = applyPattern(fields, term);

					searchSchema.groups = schema.groups;

					result.push(searchSchema);
				}
			}
		}

		router.replace({ query: query });

		table.searchQuery.value = result;
	};

	watch(table.visibleRows, () => {
		if (table.isLoading.value) {
			return;
		}

		for (let index = 0; index < values.length; index++) {
			const value = values[index];
			const error = errors[index];

			if (table.visibleRows.value.length === 0 && value) {
				error.value = "Соответствия не найдены";
			} else {
				error.value = undefined;
			}
		}
	});

	for (let index = 0; index < values.length; index++) {
		modelsOut.push({
			onInput: listeners[index],
			error: errors[index],
			placeholder: modelsIn[index].placeholder,
			style: modelsIn[index].style,
			value: ref(values[index]),
		});
	}

	onInput();

	return modelsOut;
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
