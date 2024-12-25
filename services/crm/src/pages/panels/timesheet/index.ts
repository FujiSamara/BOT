import Holidays from "date-holidays";

import { Table } from "@/components/table";
import { colors } from "@/config";
import { TimesheetSchema } from "@/types";

export class TimesheetTable extends Table<TimesheetSchema> {
	private holidays: Holidays = new Holidays("RU");

	constructor() {
		super("timesheet");

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
