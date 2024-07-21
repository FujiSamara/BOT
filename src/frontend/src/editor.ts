import axios from "axios";
import { computed, Ref, ref } from "vue";
import * as config from "@/config";

class SmartField {
	protected _rawField: Ref<any> = ref();
	protected _tipList: Ref<Array<any>> = ref([]);

	constructor(
		public name: string,
		public fieldName: string,
		defaultValue?: any,
	) {
		if (defaultValue) {
			this._rawField.value = defaultValue;
		}
	}

	protected formatter(value: any): string {
		return `${value}`;
	}
	protected async setter(newValue: any): Promise<void> {
		this._rawField.value = newValue;
	}

	public formattedField = computed({
		get: () => {
			return this.formatter(this._rawField.value);
		},
		set: async (newValue: string) => {
			await this.setter(newValue);
		},
	});

	public get rawValue() {
		return this._rawField.value;
	}

	public selectList = computed(() => {
		return this._tipList.value.map((value) => this.formatter(value));
	});

	public applySelection(index: number) {
		if (index >= this._tipList.value.length) {
			throw Error("Bad index");
		}

		this._rawField.value = this._tipList.value[index];
	}
}

class Editor {
	public fields: Array<SmartField> = [];

	public toInstanse() {
		const result: any = {};

		for (const field of this.fields) {
			result[field.fieldName] = field.rawValue;
		}

		return result;
	}
}

export class ExpenditureEditor extends Editor {
	constructor(_instance?: any) {
		super();

		if (_instance) {
			this.fields = [
				new SmartField("Статья", "name", _instance.name),
				new SmartField("Раздел", "chapter", _instance.chapter),
				new SmartField("Лимит", "limit", _instance.limit),
				new WorkerSmartField("ЦФО", "fac", _instance.fac),
				new WorkerSmartField("ЦЗ", "cc", _instance.cc),
				new WorkerSmartField(
					"Руководитель ЦЗ",
					"cc_supervisor",
					_instance.cc_supervisor,
				),
			];
		}
	}
}

class WorkerSmartField extends SmartField {
	private _endpoint: string = "";

	constructor(name: string, fieldName: string, defaultValue?: any) {
		super(name, fieldName, defaultValue);
		this._endpoint = `http://${config.backendDomain}:${config.backendPort}/${config.crmEndpoint}/worker`;
	}

	protected formatter(value: any): string {
		return `${value.l_name} ${value.f_name} ${value.o_name}`;
	}
	protected async setter(newValue: any): Promise<void> {
		const resp = await axios.get(`${this._endpoint}/find?record=${newValue}`);
		if (resp.status >= 400) {
			throw Error("Bad value");
		}

		this._tipList.value = resp.data;
		console.log(this._tipList.value);
	}
}
