import { ref, Ref } from "vue";

import { BaseEntity, SelectType } from "@/components/entity";
import { BaseSchema } from "@/types";

export interface EntityField {
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

export interface BaseEntityEditor {
	active: Ref<boolean>;
	title: Ref<string>;
	showCustom: Ref<boolean>;
	mode: Ref<EditorMode>;

	close: () => void;
	save: () => void;

	fields: EntityField[];
}

export interface EntityEditor<T extends BaseSchema> extends BaseEntityEditor {
	edit: (entity: T) => void;
	view: (entity: T) => void;
	create: () => void;
}

export function useEntityEditor<T extends BaseSchema>(
	fields: EntityField[],
	createTitle: string,
	getTitle: (model: T) => string,
	onUpdate: (model: T) => Promise<void>,
	onCreate: (model: T) => Promise<void>,
) {
	const active = ref(false);
	const title = ref("");
	const readonlyStates = fields.map((val) => val.entity.readonly as boolean);
	const mode = ref(EditorMode.View);
	const showCustom = ref(false);
	const currentModel: Ref<undefined | T> = ref(undefined);

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
		showCustom.value = false;
	};

	const load = (model: T) => {
		active.value = true;
		currentModel.value = model;

		for (const field of fields) {
			const name = field.name;
			const entity = field.entity;

			if ((model as any)[name] !== undefined && (model as any)[name] !== null) {
				entity.init((model as any)[name]);
			}
		}
	};

	const edit = (model: T) => {
		mode.value = EditorMode.Edit;
		title.value = getTitle(model);
		fields.forEach((f) => (f.entity.withTitle = true));

		load(model);
	};

	const view = (model: T) => {
		title.value = getTitle(model);
		mode.value = EditorMode.View;
		fields.forEach((f) => (f.entity.withTitle = true));

		load(model);

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
		const result: any = {};

		for (const field of fields) {
			if (!field.entity.completed.value || field.entity.readonly) continue;
			result[field.name] = field.entity.getResult();
		}

		if (mode.value === EditorMode.Create) {
			await onCreate(result);
			fields.forEach((f) => f.entity.clear());
		} else {
			if (currentModel.value !== undefined) await onUpdate(result);
		}
		active.value = false;
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
		showCustom,
	};
}
