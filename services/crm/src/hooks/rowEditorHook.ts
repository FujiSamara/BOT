import { BaseEntity, SelectType } from "@/components/entity";
import { Table } from "@/components/table";
import { BaseSchema } from "@/types";
import { Ref, ref } from "vue";

export interface RowField {
	entity: BaseEntity<any>;
	type: SelectType;
	name: string;
}

export enum EditorMode {
	Create,
	View,
	Edit,
}

export interface RowEditor {
	active: Ref<boolean>;
	close: () => void;
	save: () => void;
	edit: (index: number) => void;
	view: (index: number) => void;
	create: () => void;
	fields: RowField[];
	title: Ref<string>;
	mode: Ref<EditorMode>;
}

export function useRowEditor<T extends BaseSchema>(
	table: Table<T>,
	fields: RowField[],
	createTitle: string,
	getTitle: (model: T) => string,
): RowEditor {
	const active = ref(false);
	const title = ref("");

	const readonlyStates = fields.map((val) => val.entity.readonly as boolean);

	const mode = ref(EditorMode.View);
	let editIndex = -1;

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
		}
	};

	const load = (index: number) => {
		active.value = true;
		const model = table.getModel(index);
		editIndex = index;

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

		load(index);
	};

	const view = (index: number) => {
		title.value = getTitle(table.getModel(index));
		mode.value = EditorMode.View;

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
	};

	const save = async () => {
		active.value = false;

		const result: any = {};

		for (const field of fields) {
			if (!field.entity.completed.value) continue;
			result[field.name] = field.entity.getResult();
		}

		if (mode.value === EditorMode.Create) {
			await table.create(result);
		} else {
			await table.update(result, editIndex);
		}
	};

	return { active, close, edit, create, save, view, fields, title, mode };
}
