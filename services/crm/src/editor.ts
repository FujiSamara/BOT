import axios from "axios";
import { computed, Ref, ref, watch } from "vue";
import * as config from "@/config";
import { useNetworkStore } from "./store/network";

class SmartField {
	protected _rawField: Ref<any> = ref();

	constructor(
		public name: string,
		public fieldName: string,
		public readonly canEdit: boolean = true,
	) {}

	public get rawValue() {
		return this._rawField.value;
	}
}

export class InputSmartField extends SmartField {
	protected _tipList: Ref<Array<any>> = ref([]);
	protected _stringifyValue: Ref<string | undefined> = ref(undefined);
	private _delaySetter: number = setTimeout(() => {}, 0);
	protected readonly _delay: number = 0;
	protected _network = useNetworkStore();

	constructor(
		public name: string,
		public fieldName: string,
		defaultValue?: any,
		public readonly canEdit: boolean = true,
	) {
		super(name, fieldName, canEdit);
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
		if (newValue == "") {
			newValue = typeof this._rawField.value === "string" ? "" : undefined;
		}
		this._rawField.value = newValue;
		this._stringifyValue.value = undefined;
	}

	public formattedField = computed({
		get: () => {
			if (this._stringifyValue.value !== undefined)
				return this._stringifyValue.value;
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

export class DocumentSmartField extends SmartField {
	protected _rawField: Ref<Array<File>> = ref([]);

	public files: Ref<Array<File>> = computed({
		get: () => {
			return this._rawField.value;
		},
		set: (files) => {
			this._rawField.value = files;
		},
	});

	public get rawValue(): Array<Blob> {
		return this._rawField.value as Array<Blob>;
	}
}

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

//#region Panels editors
export class ExpenditureEditor extends Editor {
	constructor(_instance?: any) {
		super();

		this.fields = [
			new InputSmartField("Статья", "name", _instance?.name),
			new InputSmartField("Раздел", "chapter", _instance?.chapter),
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

		const chapterField = new InputSmartField(
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
			new DepartmentSmartField(
				"Производство",
				"department",
				_instance?.department,
			),
			new InputSmartField("Лимит", "limit", _instance?.limit),
		];
	}
}
export class WorkTimeEditor extends Editor {
	constructor(_instance?: any) {
		super();

		this.fields = [
			new WorkerSmartField("Работник", "worker", _instance?.worker),
			new DepartmentSmartField(
				"Производство",
				"department",
				_instance?.department,
			),
			new PostSmartField("Должность", "post", _instance?.post),
			new InputSmartField("Начало смены", "work_begin", _instance?.work_begin),
			new InputSmartField("Конец смены", "work_end", _instance?.work_end),
			new InputSmartField("День", "day", _instance?.day),
			new InputSmartField(
				"Длительность работы",
				"work_duration",
				_instance?.work_duration,
				false,
			),
			new InputSmartField("Оценка", "rating", _instance?.rating),
			new InputSmartField("Штраф", "fine", _instance?.fine),
		];
	}
}
export class BidEditor extends Editor {
	constructor(_instance?: any) {
		super();

		this.fields = [
			new InputSmartField("Cумма", "amount"),
			new PaymentTypeSmartField("Тип оплаты", "payment_type"),
			new DepartmentSmartField("Производство", "department"),
			new WorkerSmartField("Работник", "worker"),
			new InputSmartField("Цель", "purpose"),
			new DocumentSmartField("Документы", "documents"),
			new InputSmartField("Комментарий", "comment"),
		];
	}
}
//#endregion

//#region Panels smart Fields
class WorkerSmartField extends InputSmartField {
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

		const resp = await this._network.withAuthChecking(
			axios.get(`${this._endpoint}/by/name?name=${newValue}`),
		);

		this._tipList.value = resp.data;
	}
}

class ExpenditureSmartField extends InputSmartField {
	private _endpoint: string = "";
	protected readonly _delay: number = 200;

	constructor(
		name: string,
		fieldName: string,
		defaultValue?: any,
		canEdit: boolean = true,
		protected chapterField?: InputSmartField,
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

		const resp = await this._network.withAuthChecking(
			axios.get(`${this._endpoint}/find?record=${newValue}`),
		);

		this._tipList.value = resp.data;
	}
}

class DepartmentSmartField extends InputSmartField {
	private _endpoint: string = "";
	protected readonly _delay: number = 200;

	constructor(
		name: string,
		fieldName: string,
		defaultValue?: any,
		canEdit: boolean = true,
	) {
		super(name, fieldName, defaultValue, canEdit);
		this._endpoint = `${config.fullBackendURL}/${config.crmEndpoint}/department`;
	}

	protected formatter(value: any): string {
		return `${value.name}`;
	}
	protected tipFormatter(value: any): string {
		return this.formatter(value);
	}
	protected async setter(newValue: any): Promise<void> {
		if (newValue.length < 4) {
			this._tipList.value = [];
			return;
		}

		const resp = await this._network.withAuthChecking(
			axios.get(`${this._endpoint}/by/name?name=${newValue}`),
		);

		this._tipList.value = resp.data;
	}
}

class PostSmartField extends InputSmartField {
	private _endpoint: string = "";
	protected readonly _delay: number = 200;

	constructor(
		name: string,
		fieldName: string,
		defaultValue?: any,
		canEdit: boolean = true,
	) {
		super(name, fieldName, defaultValue, canEdit);
		this._endpoint = `${config.fullBackendURL}/${config.crmEndpoint}/post`;
	}

	protected formatter(value: any): string {
		return value.name;
	}
	protected tipFormatter(value: any): string {
		return this.formatter(value);
	}
	protected async setter(newValue: any): Promise<void> {
		if (newValue.length < 4) {
			this._tipList.value = [];
			return;
		}

		const resp = await this._network.withAuthChecking(
			axios.get(`${this._endpoint}/by/name?name=${newValue}`),
		);

		this._tipList.value = resp.data;
	}
}

class PaymentTypeSmartField extends InputSmartField {
	protected readonly _delay: number = 50;

	constructor(
		name: string,
		fieldName: string,
		defaultValue?: any,
		canEdit: boolean = true,
	) {
		super(name, fieldName, defaultValue, canEdit);
	}

	protected formatter(value: any): string {
		return value.name;
	}
	protected tipFormatter(value: any): string {
		return this.formatter(value);
	}
	protected async setter(newValue: any): Promise<void> {
		if (newValue.length < 4) {
			this._tipList.value = [];
			return;
		}

		this._tipList.value = ["Наличная", "Безналичная", "Требуется такси"];
	}
}

//#endregion
