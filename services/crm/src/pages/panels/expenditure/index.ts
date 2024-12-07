import { Table } from "@/components/table";
import { ExpenditureSchema } from "@/types";
import { Editor } from "@/components/table/editor";
import { InputSmartField, WorkerSmartField } from "@/components/table/field";
import * as parser from "@/parser";

export class ExpenditureTable extends Table<ExpenditureSchema> {
	constructor() {
		super("expenditure");
		this._formatters.set("fac", parser.formatWorker);
		this._formatters.set("cc", parser.formatWorker);
		this._formatters.set("paralegal", parser.formatWorker);
		this._formatters.set("creator", parser.formatWorker);
		this._formatters.set("create_date", parser.formatDateTime);

		this._aliases.set("id", "ID");
		this._aliases.set("name", "Статья");
		this._aliases.set("chapter", "Раздел");
		this._aliases.set("create_date", "Дата создания");
		this._aliases.set("fac", "ЦФО");
		this._aliases.set("cc", "ЦЗ");
		this._aliases.set("paralegal", "Юрисконсульт");
		this._aliases.set("creator", "Создал");
	}
}

export class ExpenditureEditor extends Editor {
	constructor(_instance?: any) {
		super();

		this.fields = [
			new InputSmartField("Статья", "name", _instance?.name),
			new InputSmartField("Раздел", "chapter", _instance?.chapter),
			new WorkerSmartField("ЦФО", "fac", _instance?.fac),
			new WorkerSmartField("ЦЗ", "cc", _instance?.cc),
			new WorkerSmartField("Юрисконсульт", "paralegal", _instance?.paralegal),
		];
	}
}
