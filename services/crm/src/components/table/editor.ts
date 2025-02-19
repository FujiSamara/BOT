import { useNetworkStore } from "@/store/network";
import { SmartField } from "@/components/table/field.ts";

export class Editor {
	public fields: Array<SmartField> = [];
	protected _network = useNetworkStore();

	public toInstanse() {
		const result: any = {};
		for (const field of this.fields) {
			result[field.fieldName] = field.rawValue;
		}
		return result;
	}
}
