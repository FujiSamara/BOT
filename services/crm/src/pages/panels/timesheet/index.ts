import { Table } from "@/components/table";
import { TimesheetSchema } from "@/types";

export class TimesheetTable extends Table<TimesheetSchema> {
	constructor() {
		super("timesheet");

		this._aliases.set("worker_fullname", "Работник");
		this._aliases.set("post_name", "Должность");
		this._aliases.set("total_hours", "Всего отработано");
	}
}
