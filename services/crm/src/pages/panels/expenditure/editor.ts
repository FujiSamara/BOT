import { Editor } from "@/components/table/editor";
import { InputSmartField, WorkerSmartField } from "@/components/table/field";

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
