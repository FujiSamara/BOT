import Holidays from "date-holidays";

import { Table } from "@/components/table";
import { colors } from "@/config";
import { RouteData, TimesheetSchema } from "@/types";
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

interface TimesheetPanelData {
	searchList: SearchModelOut[];
	entitySearchList: EntitySearchModelOut;
	dateInterval: DateIntervalModelOut;
}

export class TimesheetTable extends Table<TimesheetSchema> {
	private holidays: Holidays = new Holidays("RU");

	constructor() {
		super("timesheet");

		this._formatters.set("total_hours", parser.formatFloat);
		for (let index = 1; index < 32; index++) {
			this._formatters.set(index.toString(), parser.formatFloat);
		}

		this._aliases.set("id", "ID");
		this._aliases.set("worker_fullname", "Работник");
		this._aliases.set("post_name", "Должность");
		this._aliases.set("department_name", "Предприятие");
		this._aliases.set("total_hours", "Всего отработано");

		this._columsOrder.set("id", 0);
		this._columsOrder.set("worker_fullname", 1);
		this._columsOrder.set("post_name", 2);
		this._columsOrder.set("department_name", 3);
		this._columsOrder.set("total_hours", 4);
	}

	public orderDisabled(header: string): boolean {
		let status = this.getAlias("total_hours") === header;

		for (let index = 1; index < 32; index++) {
			status ||= index.toString() === header;
		}

		return status;
	}

	public getHeaderColor(alias: string): string | undefined {
		let num = parseInt(alias);

		if (isNaN(num)) return;
		const start = this.byDate.value!.start;
		const date = new Date(start.getFullYear(), start.getMonth(), num, 10);
		if (this.holidays.isHoliday(date) || date.getDay() % 6 === 0)
			return colors.holiday;
	}
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
	const dateInterval = await useDateInterval(table, "", routeData);

	return {
		entitySearchList,
		searchList,
		dateInterval,
	};
}
