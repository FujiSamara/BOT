import { Table } from "@/components/table";
import {
	RouteData,
	WorkTimeSchema,
	WorkTimeSchema as WorktimeSchema,
} from "@/types";
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
	DateEntity,
	TimeEntity,
} from "@/components/entity";
import { RowEditor, RowField, useRowEditor } from "@/hooks/rowEditorHook";

interface WorktimePanelData {
	searchList: SearchModelOut[];
	entitySearchList: EntitySearchModelOut;
	dateInterval: DateIntervalModelOut;
	rowEditor: RowEditor<WorkTimeSchema>;
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

	public orderDisabled(header: string): boolean {
		return ["Фото"].includes(header);
	}
}

export function getWorktimeEditorFields(): RowField[] {
	return [
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
			entity: new TimeEntity(true, "Начало смены"),
			type: SelectType.Time,
			name: "work_begin",
		},
		{
			entity: new TimeEntity(false, "Конец смены"),
			type: SelectType.Time,
			name: "work_end",
		},
		{
			entity: new DateEntity(true, "День"),
			type: SelectType.Date,
			name: "day",
		},
		{
			entity: new FloatInputEntity(false, "Оценка"),
			type: SelectType.Input,
			name: "rating",
		},
		{
			entity: new FloatInputEntity(false, "Штраф"),
			type: SelectType.Input,
			name: "fine",
		},
	];
}

export async function setupWorktime(
	table: WorktimeTable,
	routeData: RouteData,
): Promise<WorktimePanelData> {
	const searchList = await useSearch(table, routeData, {
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
	const entitySearchList = await useEntitySearch(
		table,
		routeData,
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
	const dateInterval = await useDateInterval(table, "day", routeData);
	const rowEditor = useRowEditor<WorktimeSchema, WorktimeTable>(
		table,
		getWorktimeEditorFields(),
		"Создать явку",
		(_) => "Изменить явку",
	);

	return {
		entitySearchList,
		searchList,
		dateInterval,
		rowEditor,
	};
}
