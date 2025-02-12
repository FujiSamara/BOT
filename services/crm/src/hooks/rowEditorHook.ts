import { BaseEntity, SelectType } from "@/components/entity";
import { Table } from "@/components/table";
import { BaseSchema } from "@/types";
import { Ref, ref } from "vue";

export interface RowField {
	entity: BaseEntity<any>;
	type: SelectType;
	name: string;
	active?: boolean;
}

export enum EditorMode {
	Create,
	View,
	Edit,
}

export interface RowEditor<T extends BaseSchema> {
	active: Ref<boolean>;
	close: () => void;
	save: () => void;
	edit: (index: number) => void;
	view: (index: number) => void;
	create: () => void;
	fields: RowField[];
	title: Ref<string>;
	mode: Ref<EditorMode>;
	modelIndex: Ref<number | undefined>;
	table: Table<T>;
}

export function useRowEditor<T extends BaseSchema>(
	table: Table<T>,
	fields: RowField[],
	createTitle: string,
	getTitle: (model: T) => string,
): RowEditor<T> {
	const active = ref(false);
	const title = ref("");
	const modelIndex: Ref<number | undefined> = ref(undefined);
	const readonlyStates = fields.map((val) => val.entity.readonly as boolean);
	const mode = ref(EditorMode.View);

	fields.forEach((f) => (f.active = true));

	const close = () => {
		active.value = false;

		switch (mode.value) {
			case EditorMode.View:
				for (let index = 0; index < fields.length; index++) {
					const field = fields[index];
					field.entity.readonly = readonlyStates[index];
				}
				fields.forEach((f) => f.entity.clear());
				break;
			case EditorMode.Edit:
				fields.forEach((f) => f.entity.clear());
				break;
			case EditorMode.Create:
				fields.forEach((f) => (f.active = true));
				break;
		}
		fields.forEach((f) => (f.entity.withTitle = false));
	};

	const load = (index: number) => {
		active.value = true;
		const model = table.getModel(index);
		modelIndex.value = index;

		for (const field of fields) {
			const name = field.name;
			const entity = field.entity;

			if ((model as any)[name] !== undefined && (model as any)[name] !== null) {
				entity.init((model as any)[name]);
			}
		}
	};

	const edit = (index: number) => {
		mode.value = EditorMode.Edit;
		title.value = getTitle(table.getModel(index));
		fields.forEach((f) => (f.entity.withTitle = true));

		load(index);
	};

	const view = (index: number) => {
		title.value = getTitle(table.getModel(index));
		mode.value = EditorMode.View;
		fields.forEach((f) => (f.entity.withTitle = true));

		load(index);

		for (let index = 0; index < fields.length; index++) {
			const field = fields[index];

			readonlyStates[index] = field.entity.readonly as boolean;
			field.entity.readonly = true;
		}
	};

	const create = () => {
		active.value = true;
		title.value = createTitle;
		mode.value = EditorMode.Create;

		for (const field of fields) {
			field.active = !field.entity.readonly;
			field.entity.withTitle = true;
		}
	};

	const save = async () => {
		active.value = false;

		const result: any = {};

		for (const field of fields) {
			if (!field.entity.completed.value || field.entity.readonly) continue;
			result[field.name] = field.entity.getResult();
		}

		if (mode.value === EditorMode.Create) {
			await table.create(result);
		} else {
			if (modelIndex.value) await table.update(result, modelIndex.value);
		}
	};

	return {
		active,
		close,
		edit,
		create,
		save,
		view,
		fields,
		title,
		mode,
		modelIndex,
		table,
	};
}
