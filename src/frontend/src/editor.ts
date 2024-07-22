import axios from "axios";
import { computed, Ref, ref } from "vue";
import * as config from "@/config";

class SmartField {
	protected _rawField: Ref<any> = ref();
	protected _tipList: Ref<Array<any>> = ref([]);
	private _delaySetter: number = setTimeout(() => {}, 0);
	protected _stringifyValue: Ref<string | undefined> = ref(undefined);

	constructor(
		public name: string,
		public fieldName: string,
		defaultValue?: any,
		private _delay: number = 0,
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
		this._stringifyValue.value = undefined;
	}

	public formattedField = computed({
		get: () => {
			if (this._stringifyValue.value) return this._stringifyValue.value;
			if (this._rawField.value === undefined) return "";
			return this.formatter(this._rawField.value);
		},
		set: async (newValue: string) => {
			this._stringifyValue.value = newValue;
			clearTimeout(this._delaySetter);
			this._delaySetter = setTimeout(async () => {
				await this.setter(newValue);
			}, this._delay);
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

		this._stringifyValue.value = undefined;
		this._rawField.value = this._tipList.value[index];
		this._tipList.value = [];
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

		this.fields = [
			new SmartField("Статья", "name", _instance?.name),
			new SmartField("Раздел", "chapter", _instance?.chapter),
			new SmartField("Лимит", "limit", _instance?.limit),
			new WorkerSmartField("ЦФО", "fac", _instance?.fac),
			new WorkerSmartField("ЦЗ", "cc", _instance?.cc),
			new WorkerSmartField(
				"Руководитель ЦЗ",
				"cc_supervisor",
				_instance?.cc_supervisor,
			),
		];
	}
}

class WorkerSmartField extends SmartField {
	private _endpoint: string = "";

	constructor(name: string, fieldName: string, defaultValue?: any) {
		super(name, fieldName, defaultValue, 200);
		this._endpoint = `${config.fullBackendURL}}/${config.crmEndpoint}/worker`;
	}

	protected formatter(value: any): string {
		return `${value.l_name} ${value.f_name} ${value.o_name}`;
	}
	protected async setter(newValue: any): Promise<void> {
		if (newValue.length < 4) {
			this._tipList.value = [];
			return;
		}

		const resp = await axios.get(`${this._endpoint}/find?record=${newValue}`);

		this._tipList.value = resp.data;
	}
}
