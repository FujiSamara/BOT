import { Table } from "@/components/table";
import { BaseSchema, WorkTimeSchema as WorktimeSchema } from "@/types";
import { Editor } from "@/components/table/editor";
import {
	DateTimeSmartField,
	DepartmentSmartField,
	InputSmartField,
	PostSmartField,
	WorkerSmartField,
} from "@/components/table/field";
import * as parser from "@/parser";
import {
	EntitySearchModelOut,
	SearchModelOut,
	useSearch,
	useEntitySearch,
} from "@/hooks/tableSearchHook";
import {
	DateIntervalModelOut,
	useDateInterval,
} from "@/hooks/dateIntervalHook";
import {
	DepartmentEntity,
	FloatInputEntity,
	PostEntity,
	SelectType,
	WorkerEntity,
} from "@/components/entity";
import { RowEditor, useRowEditor } from "@/hooks/rowEditorHook";

interface WorktimePanelData {
	searchList: SearchModelOut[];
	entitySearchList: EntitySearchModelOut;
	dateInterval: DateIntervalModelOut;
	rowEditor: RowEditor;
}

export class WorktimeTable extends Table<WorktimeSchema> {
	constructor() {
		super("worktime");
		this._formatters.set("worker", parser.formatWorker);
		this._formatters.set("department", parser.formatDepartment);
		this._formatters.set("post", parser.formatPost);
		this._formatters.set("work_begin", parser.formatTime);
		this._formatters.set("work_end", parser.formatTime);
		this._formatters.set("day", parser.formatDate);
		this._formatters.set("photo_b64", parser.formatWorkTimePhoto);
		this._formatters.set("work_duration", parser.formatFloat);

		this._aliases.set("id", "ID");
		this._aliases.set("worker", "Работник");
		this._aliases.set("department", "Производство");
		this._aliases.set("post", "Должность");
		this._aliases.set("work_begin", "Начало смены");
		this._aliases.set("work_end", "Конец смены");
		this._aliases.set("day", "День");
		this._aliases.set("work_duration", "Длительность");
		this._aliases.set("rating", "Оценка");
		this._aliases.set("fine", "Штраф");
		this._aliases.set("photo_b64", "Фото");
	}
}

export async function setupWorktime(
	table: Table<BaseSchema>,
): Promise<WorktimePanelData> {
	const searchList = useSearch(table, {
		schemas: [
			{
				pattern: "worker",
				groups: [0],
			},
		],
		placeholder: "Поиск",
		style: "height: 100%; width: 170px",
		name: "general",
	});
	const entitySearchList = useEntitySearch(
		table,
		{
			entity: new DepartmentEntity(),
			pattern: "department",
			groups: [0],
			id: 0,
		},
		{
			entity: new PostEntity(),
			pattern: "post",
			groups: [1],
			id: 1,
		},
	);
	const dateInterval = await useDateInterval(table, "day");
	const rowEditor = useRowEditor(
		table,
		[
			{
				entity: new WorkerEntity(true, true),
				type: SelectType.MonoSelectInput,
				name: "worker",
			},
			{
				entity: new DepartmentEntity(true, true),
				type: SelectType.MonoSelectInput,
				name: "department",
			},
			{
				entity: new PostEntity(true, true),
				type: SelectType.MonoSelectInput,
				name: "post",
			},
			{
				entity: new FloatInputEntity(false, "Оценка"),
				type: SelectType.Input,
				name: "rate",
			},
			{
				entity: new FloatInputEntity(false, "Штраф"),
				type: SelectType.Input,
				name: "fine",
			},
		],
		"Создать явку",
		"Изменить явку",
	);

	return {
		entitySearchList,
		searchList,
		dateInterval,
		rowEditor,
	};
}

export class WorkTimeEditor extends Editor {
	constructor(_instance?: any) {
		super();
		this.fields = [
			new WorkerSmartField("Работник", "worker", _instance?.worker, true, true),
			new DepartmentSmartField(
				"Производство",
				"department",
				_instance?.department,
				true,
				true,
			),
			new PostSmartField("Должность", "post", _instance?.post, true, true),
			new DateTimeSmartField(
				"Начало смены",
				"work_begin",
				_instance?.work_begin,
				true,
				true,
			),
			new DateTimeSmartField("Конец смены", "work_end", _instance?.work_end),
			new DateTimeSmartField("День", "day", _instance?.day, true, true, "date"),
			new InputSmartField(
				"Длительность работы",
				"work_duration",
				_instance?.work_duration,
				false,
			),
			new InputSmartField("Оценка", "rating", _instance?.rating),
			new InputSmartField("Штраф", "fine", _instance?.fine),
		];
	}
}
