import { Table } from "@/components/table";
import { TimesheetSchema } from "@/types";

export class TimesheetTable extends Table<TimesheetSchema> {
	constructor() {
		super("timesheet");

		this._aliases.set("id", "Айди работника");
		this._aliases.set("worker_fullname", "Работник");
		this._aliases.set("post_name", "Должность");
		this._aliases.set("total_hours", "Всего отработано");

		this._columsOrder.set("id", 0);
		this._columsOrder.set("worker_fullname", 1);
		this._columsOrder.set("post_name", 2);
		this._columsOrder.set("total_hours", 3);
	}

	public orderDisabled(header: string): boolean {
		let status = this.getAlias("total_hours") === header;

		for (let index = 1; index < 32; index++) {
			status ||= index.toString() === header;
		}

		return status;
	}
}
