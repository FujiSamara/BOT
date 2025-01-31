import { BaseEntity, SelectType } from "@/components/entity";
import { BaseSchema } from "@/types";
import { Ref, ref } from "vue";

export interface RowField {
	entity: BaseEntity<any>;
	type: SelectType;
	name: string;
}

export interface RowEditor {
	active: Ref<boolean>;
	close: () => void;
	save: () => void;
	edit: (model: BaseSchema) => void;
	create: () => void;
	fields: RowField[];
	title: Ref<string>;
}

export const useRowEditor = (
	fields: RowField[],
	createTitle: string,
	editTitle: string,
): RowEditor => {
	const active = ref(false);
	const title = ref("");
	const isCreating = ref(false);

	const close = () => {
		active.value = false;
		if (!isCreating.value) {
			fields.forEach((f) => f.entity.clear());
		}
	};

	const edit = (model: BaseSchema) => {
		active.value = true;
		title.value = editTitle;
		isCreating.value = false;

		for (const field of fields) {
			const name = field.name;
			const entity = field.entity;

			entity.init((model as any)[name]);
		}
	};

	const create = () => {
		active.value = true;
		title.value = createTitle;
		isCreating.value = true;
	};

	const save = () => {
		active.value = false;
	};

	return { active, close, edit, create, save, fields, title };
};
