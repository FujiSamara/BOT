import { BaseEntity, InputSelectEntity } from "@/components/entity";
import { Table } from "@/components/table";
import { BaseSchema, FilterSchema, RouteData, SearchSchema } from "@/types";
import { nextTick, Ref, ref, watch } from "vue";
import { base64UrlDecode, base64UrlEncode } from "@/parser";

export interface SearchModelIn {
	schemas: {
		pattern: string; // Pattern in format: parent.child.grandson...
		groups: number[];
	}[];
	name: string;
	style?: string;
	placeholder?: string;
}

export interface SearchModelOut {
	onInput: (value: string) => void;
	style?: string;
	placeholder?: string;
	error: Ref<string | undefined>;
	value: Ref<string>;
}

export const useSearch = async (
	table: Table<BaseSchema>,
	routeData: RouteData,
	...modelsIn: SearchModelIn[]
): Promise<SearchModelOut[]> => {
	const values = modelsIn.map((_) => "");
	const errors: Ref<string | undefined>[] = modelsIn.map((_) => ref(undefined));
	const modelsOut: SearchModelOut[] = [];
	const neededLetter = 3;
	const listeners = modelsIn.map((_, index) => {
		const onModelChanged = (value: string) => {
			modelsOut[index].value.value = value;
			values[index] = value;
			onInput();
		};
		return onModelChanged;
	});

	const route = routeData.route;
	const router = routeData.router;

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

			if (term.length && term.length < neededLetter) {
				errors[index].value = `Необходимо минимум ${neededLetter} символа`;
				continue;
			}

			for (const schema of modelIn.schemas) {
				const fields = schema.pattern.split(".");

				const searchSchema = applyPattern(fields, term);

				searchSchema.groups = schema.groups;

				result.push(searchSchema);
			}
		}
		await router.replace({ query: query });
		await nextTick();
		if (result.length === 0 && table.searchQuery.value.length === 0) return;

		table.searchQuery.value = result;
	};

	watch(table.visibleRows, () => {
		if (table.isLoading.value) {
			return;
		}

		for (let index = 0; index < values.length; index++) {
			const value = values[index];
			const error = errors[index];

			let newError = undefined;

			if (value) {
				if (table.visibleRows.value.length === 0) {
					newError = "Совпадения не найдены";
				} else if (value.length < neededLetter) {
					newError = `Необходимо минимум ${neededLetter} символа`;
				}
			}
			error.value = newError;
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

	await onInput();

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

export interface EntitySearchModelIn<
	T extends BaseSchema,
	E extends InputSelectEntity<T>,
> {
	pattern: string; // Pattern in format: parent.child.grandson...
	groups: number[];
	entity: E;
	filter?: (entity: T) => FilterSchema | FilterSchema[]; // Custom filter for entity
	id: number;
}

export interface EntitySearchModelOut {
	entities: BaseEntity<BaseSchema>[];
	exist: Ref<boolean>;
}

export const useEntitySearch = async (
	table: Table<BaseSchema>,
	routeData: RouteData,
	...modelsIn: EntitySearchModelIn<any, InputSelectEntity<any>>[]
): Promise<EntitySearchModelOut> => {
	const modelOut: EntitySearchModelOut = {
		entities: modelsIn.map((val) => val.entity),
		exist: ref(false),
	};

	const route = routeData.route;
	const router = routeData.router;

	const serializeEntitySearchFilter = () => {
		let result = "";

		for (const modelIn of modelsIn) {
			const selected = modelIn.entity.selectedEntities.value;

			for (const entity of selected) {
				result += `${modelIn.id}=${entity.id};`;
			}
		}

		return base64UrlEncode(result);
	};

	const loadSerializedSearch = async (payload: string) => {
		const decoded = base64UrlDecode(payload);
		const data = decoded
			.split(";")
			.filter((val) => val)
			.map((val) => {
				const field = val.split("=");

				return { modelId: parseInt(field[0]), entityId: parseInt(field[1]) };
			});

		for (const modelIn of modelsIn) {
			const filters = data.filter((val) => val.modelId === modelIn.id);

			for (const filter of filters) {
				await modelIn.entity.load(filter.entityId);
			}
		}
	};

	const loadQuery = async () => {
		const query = { ...route.query };

		if ("entitySearch" in query) {
			const payload = query["entitySearch"] as string;
			try {
				await loadSerializedSearch(payload);
			} catch (e) {
				console.log(e);
				delete query["entitySearch"];
				return;
			}
		}
	};
	const saveQuery = async () => {
		const query = { ...route.query };

		query["entitySearch"] = serializeEntitySearchFilter();

		if (query["entitySearch"] === "") {
			delete query["entitySearch"];
		}

		await router.replace({ query: query });
	};

	for (let index = 0; index < modelsIn.length; index++) {
		const modelIn = modelsIn[index];
		watch(modelIn.entity.selectedEntities, async () => {
			const selected = modelIn.entity.selectedEntities.value;
			const filters: FilterSchema[] = [];

			for (const entity of selected) {
				let filter = [];

				if (modelIn.filter) {
					const res = modelIn.filter(entity);
					if (res instanceof Array) {
						filter.push(...res);
					} else {
						filter.push(res);
					}
				} else {
					const fields = [...modelIn.pattern.split("."), "id"];
					filter.push(applyFilterPattern(fields, entity.id));
				}

				filter.forEach((fil) => {
					fil.groups = modelIn.groups;
					fil.id = modelIn.id;
				});

				filters.push(...filter);
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

			const tempSet = new Set(
				temp.map((val) => (val.id === undefined ? -1 : val.id)),
			);
			const idSet = new Set(modelsIn.map((val) => val.id));

			modelOut.exist.value = tempSet.intersection(idSet).size > 0;
			table.filterQuery.value = temp;

			await saveQuery();
		});
	}

	await loadQuery();

	return modelOut;
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
