import { BaseEntity, SelectType } from "@/components/entity";
import { BaseSchema } from "@/types";
import { Ref, ref } from "vue";

export interface RowField {
	entity: BaseEntity<any>;
	type: SelectType;
}

export interface RowEditor {
	active: Ref<boolean>;
	close: () => void;
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

	const close = () => {
		active.value = false;
	};

	const edit = (model: BaseSchema) => {
		active.value = true;
		title.value = editTitle;
	};

	const create = () => {
		active.value = true;
		title.value = createTitle;
	};

	return { active, close, edit, create, fields, title };
};
