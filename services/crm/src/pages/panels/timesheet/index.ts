import Holidays from "date-holidays";

import { Table } from "@/components/table";
import { colors } from "@/config";
import {
	RouteData,
	ShiftDurationSchema,
	TimesheetSchema,
	WorkTimeSchema,
} from "@/types";
import {
	DateIntervalModelOut,
	useDateInterval,
} from "@/hooks/dateIntervalHook";
import {
	EntitySearchModelOut,
	SearchModelOut,
	useEntitySearch,
	useSearch,
} from "@/hooks/tableSearchHook";
import { DepartmentEntity, PostEntity } from "@/components/entity";
import * as parser from "@/parser";
import { BaseEntityEditor, useEntityEditor } from "@/hooks/entityEditorHook";
import { getWorktimeEditorFields } from "@/pages/panels/worktime";
import EntityService from "@/services/entity";

export class TimesheetTable extends Table<TimesheetSchema> {
	private holidays: Holidays = new Holidays("RU");

	constructor() {
		super("timesheet");

		this._formatters.set("total_shifts", parser.formatInt);
		this._formatters.set("total_hours", parser.formatFloatTime);
		for (let index = 1; index < 32; index++) {
			this._formatters.set(index.toString(), parser.formatShiftDuration);
		}

		this._aliases.set("id", "ID");
		this._aliases.set("worker_fullname", "Работник");
		this._aliases.set("post_name", "Должность");
		this._aliases.set("department_name", "Предприятие");
		this._aliases.set("total_hours", "Всего отработано");
		this._aliases.set("total_shifts", "Всего смен");
		for (let index = 1; index < 32; index++) {
			this._aliases.set(index.toString(), () =>
				this.formatDateHeader(index.toString()),
			);
		}

		this._columsOrder.set("id", 0);
		this._columsOrder.set("worker_fullname", 1);
		this._columsOrder.set("post_name", 2);
		this._columsOrder.set("department_name", 3);
		this._columsOrder.set("total_hours", 4);
		this._columsOrder.set("total_shifts", 5);
	}

	private formatDateHeader(day: string): string {
		const date = this.toDate(day);

		if (date === undefined) return "";

		const dayOfWeek = date.getDay();
		const str: any = {
			0: "ВС",
			1: "ПН",
			2: "ВТ",
			3: "СР",
			4: "ЧТ",
			5: "ПТ",
			6: "СБ",
		};

		return `${date.getDate()}\n${str[dayOfWeek]}`;
	}

	public orderDisabled(header: string): boolean {
		let status = this.getAlias("total_hours") === header;

		for (let index = 1; index < 32; index++) {
			status ||= this.formatDateHeader(index.toString()) === header;
		}

		return status;
	}

	private toDate(stringNum: string): Date | undefined {
		let num = parseInt(stringNum);
		if (isNaN(num)) return;
		if (this.byDate.value === undefined) return;
		const start = this.byDate.value.start;
		const date = new Date(start.getFullYear(), start.getMonth(), num, 10);
		return date;
	}

	public getHeaderColor(alias: string): string | undefined {
		const date = this.toDate(alias);
		if (date === undefined) return;
		if (this.holidays.isHoliday(date) || date.getDay() % 6 === 0)
			return colors.holiday;
	}
}

export interface TimesheetEditor extends BaseEntityEditor {
	edit: (rowIndex: number, cellIndex: number) => void;
	create: () => void;
}

export function useTimesheetEditor(table: TimesheetTable) {
	const service = new EntityService<WorkTimeSchema>("worktime");

	const onUpdate = async (worktime: WorkTimeSchema) => {};
	const onCreate = async (worktime: WorkTimeSchema) => {};

	const editor = useEntityEditor(
		getWorktimeEditorFields(),
		"Создать Явку",
		(_) => "Изменить явку",
		onUpdate,
		onCreate,
	);

	const edit = (rowIndex: number, cellIndex: number) => {
		const model = table.getModel(rowIndex);
		const fieldName = table.getFieldName(cellIndex);

		const num = parseInt(fieldName);
		if (isNaN(num)) return;

		const shift_duration = model[fieldName];

		if (typeof shift_duration === "number") return;

		const worktime_id = (shift_duration as ShiftDurationSchema).worktime_id;

		console.log(worktime_id);
	};

	return {
		active: editor.active,
		close: editor.close,
		edit,
		create: editor.create,
		save: editor.save,
		fields: editor.fields,
		title: editor.title,
		mode: editor.mode,
		showCustom: editor.showCustom,
	};
}

interface TimesheetPanelData {
	searchList: SearchModelOut[];
	entitySearchList: EntitySearchModelOut;
	dateInterval: DateIntervalModelOut;
	rowEditor: TimesheetEditor;
}

export async function setupTimesheet(
	table: TimesheetTable,
	routeData: RouteData,
): Promise<TimesheetPanelData> {
	const searchList = await useSearch(table, routeData, {
		schemas: [
			{
				pattern: "l_name",
				groups: [0],
			},
			{
				pattern: "f_name",
				groups: [1],
			},
			{
				pattern: "o_name",
				groups: [2],
			},
			{
				pattern: "post",
				groups: [3],
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
	const dateInterval = await useDateInterval(table, "", routeData);
	const rowEditor = useTimesheetEditor(table);

	return {
		entitySearchList,
		searchList,
		dateInterval,
		rowEditor,
	};
}
