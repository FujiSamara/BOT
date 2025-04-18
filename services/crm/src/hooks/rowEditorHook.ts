import { Ref, ref } from "vue";

import { Table } from "@/components/table";
import { BaseSchema } from "@/types";
import {
	EntityField,
	useEntityEditor,
	BaseEntityEditor,
} from "@/hooks/entityEditorHook";

export interface RowField extends EntityField {}

export interface RowEditor<T extends BaseSchema> extends BaseEntityEditor {
	edit: (index: number) => void;
	view: (index: number) => void;
	create: () => void;

	fields: RowField[];
	modelIndex: Ref<number | undefined>;
	table: Table<T>;
}

export function useRowEditor<S extends BaseSchema, T extends Table<S>>(
	table: T,
	fields: RowField[],
	createTitle: string,
	getTitle: (model: S) => string,
): RowEditor<S> {
	const modelIndex: Ref<number | undefined> = ref(undefined);

	const onCreate = async (model: S) => {
		await table.create(model);
	};

	const onUpdate = async (model: S) => {
		if (modelIndex.value !== undefined)
			await table.update(model, modelIndex.value);
	};

	const editor = useEntityEditor(
		fields,
		createTitle,
		getTitle,
		onUpdate,
		onCreate,
	);

	const edit = (index: number) => {
		const model = table.getModel(index);
		modelIndex.value = index;
		editor.edit(model);
	};

	const view = (index: number) => {
		const model = table.getModel(index);
		modelIndex.value = index;
		editor.view(model);
	};

	return {
		active: editor.active,
		close: editor.close,
		edit,
		create: editor.create,
		save: editor.save,
		view,
		fields,
		title: editor.title,
		mode: editor.mode,
		modelIndex,
		table,
		showCustom: editor.showCustom,
	};
}
