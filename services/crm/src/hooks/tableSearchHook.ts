import { BaseEntity } from "@/components/entity";
import { Table } from "@/components/table";
import { BaseSchema, FilterSchema, SearchSchema } from "@/types";
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

	const onInput = async () => {
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
		await router.replace({ query: query });

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

interface EntitySearchModelIn {
	pattern: string; // Pattern in format: parent.child.grandson...
	groups: number[];
	entity: BaseEntity<BaseSchema>;
	id: number;
}

interface EntitySearchModelOut {
	entities: BaseEntity<BaseSchema>[];
}

export const useEntitySearch = (
	table: Table<BaseSchema>,
	...modelsIn: EntitySearchModelIn[]
): EntitySearchModelOut => {
	const modelsOut: EntitySearchModelOut = {
		entities: modelsIn.map((val) => val.entity),
	};

	for (let index = 0; index < modelsIn.length; index++) {
		const modelIn = modelsIn[index];
		watch(modelIn.entity.selectedEntities, () => {
			const selected = modelIn.entity.selectedEntities.value;
			const filters: FilterSchema[] = [];

			for (const entity of selected) {
				const fields = [...modelIn.pattern.split("."), "id"];

				const filter = applyFilterPattern(fields, entity.id);
				filter.groups = modelIn.groups;
				filter.id = modelIn.id;

				filters.push(filter);
			}

			const temp = [...table.filterQuery.value];

			const oldIndexes = [];

			for (let i = 0; i < temp.length; i++) {
				const oldFilter = temp[i];

				if (modelIn.id === oldFilter.id) {
					oldIndexes.push(i);
				}
			}

			oldIndexes.sort((a, b) => b - a);

			for (const index of oldIndexes) {
				temp.splice(index, 1);
			}

			for (const filter of filters) {
				temp.push(filter);
			}

			table.filterQuery.value = temp;
		});
	}

	return modelsOut;
};

const applyFilterPattern = (fields: string[], value: any): FilterSchema => {
	const deps = [];
	let completedTerm = value;

	if (fields.length > 1) {
		completedTerm = "";
		deps.push(applyFilterPattern(fields.slice(1), value));
	}

	const result: FilterSchema = {
		column: fields[0],
		value: completedTerm,
		dependencies: deps,
	};

	return result;
};
