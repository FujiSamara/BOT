import axios from "axios";
import { computed, Ref, ref, watch } from "vue";
import * as config from "@/config";

class SmartField {
	protected _rawField: Ref<any> = ref();
	protected _tipList: Ref<Array<any>> = ref([]);
	private _delaySetter: number = setTimeout(() => {}, 0);
	protected _stringifyValue: Ref<string | undefined> = ref(undefined);
	protected readonly _delay: number = 0;

	constructor(
		public name: string,
		public fieldName: string,
		defaultValue?: any,
		public readonly canEdit: boolean = true,
	) {
		if (defaultValue) {
			this._rawField.value = defaultValue;
		}
	}

	protected formatter(value: any): string {
		return `${value}`;
	}
	protected tipFormatter(value: any): string {
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
		return this._tipList.value.map((value) => this.tipFormatter(value));
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

//#region Panels editors
export class ExpenditureEditor extends Editor {
	constructor(_instance?: any) {
		super();

		this.fields = [
			new SmartField("Статья", "name", _instance?.name),
			new SmartField("Раздел", "chapter", _instance?.chapter),
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

export class BudgetEditor extends Editor {
	constructor(_instance?: any) {
		super();

		const chapterField = new SmartField(
			"Раздел",
			"chapter",
			_instance?.expenditure.chapter,
			false,
		);

		this.fields = [
			chapterField,
			new ExpenditureSmartField(
				"Статья",
				"expenditure",
				_instance?.expenditure,
				true,
				chapterField,
			),
			new SmartField("Лимит", "limit", _instance?.limit),
		];
	}
}
//#endregion

//#region Panels smart Fields
class WorkerSmartField extends SmartField {
	private _endpoint: string = "";
	protected readonly _delay: number = 200;

	constructor(
		name: string,
		fieldName: string,
		defaultValue?: any,
		canEdit: boolean = true,
	) {
		super(name, fieldName, defaultValue, canEdit);
		this._endpoint = `${config.fullBackendURL}/${config.crmEndpoint}/worker`;
	}

	protected formatter(value: any): string {
		return `${value.l_name} ${value.f_name} ${value.o_name}`;
	}
	protected tipFormatter(value: any): string {
		return this.formatter(value);
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

class ExpenditureSmartField extends SmartField {
	private _endpoint: string = "";
	protected readonly _delay: number = 200;

	constructor(
		name: string,
		fieldName: string,
		defaultValue?: any,
		canEdit: boolean = true,
		protected chapterField?: SmartField,
	) {
		super(name, fieldName, defaultValue, canEdit);
		this._endpoint = `${config.fullBackendURL}/${config.crmEndpoint}/expenditure`;
		if (chapterField) {
			watch(this._rawField, () => {
				chapterField.formattedField.value = this._rawField.value.chapter;
			});
		}
	}

	protected formatter(value: any): string {
		return `${value.name}`;
	}
	protected tipFormatter(value: any): string {
		return `${value.name}/${value.chapter}`;
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
//#endregion
