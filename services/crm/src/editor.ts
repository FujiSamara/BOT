import axios from "axios";
import { computed, Ref, ref, watch } from "vue";
import * as config from "@/config";
import { useNetworkStore } from "./store/network";
import { DocumentSchema } from "./types";
import * as parser from "@/parser";

export class SmartField {
	protected _rawField: Ref<any> = ref();
	public completed: Ref<boolean> = ref(false); // indicates completed field or not.

	constructor(
		public name: string,
		public fieldName: string,
		public readonly canEdit: boolean = true,
		public readonly required: boolean = false,
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
		public readonly required: boolean = false,
		public readonly simple: boolean = true,
	) {
		super(name, fieldName, canEdit, required);
		if (defaultValue) {
			this._rawField.value = defaultValue;
			this.completed.value = true;
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
			this.completed.value = this.simple && newValue.length !== 0;
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

	public rawSelectList = computed(() => {
		return this._tipList.value;
	});

	public applySelection(index: number) {
		if (index >= this._tipList.value.length) {
			throw Error("Bad index");
		}

		this._stringifyValue.value = undefined;
		this._rawField.value = this._tipList.value[index];
		this._tipList.value = [];
		this.completed.value = true;
	}
}

export class DocumentSmartField extends SmartField {
	protected _rawField: Ref<Array<DocumentSchema>> = ref([]);
	public files: Ref<Array<File>> = ref([]);

	constructor(
		public name: string,
		public fieldName: string,
		public readonly canEdit: boolean = true,
		public readonly required: boolean = false,
	) {
		super(name, fieldName, canEdit, required);

		watch(this.files.value, async () => {
			this.completed.value = this.files.value.length !== 0;

			const files = [];
			for (let index = 0; index < this.files.value.length; index++) {
				const doc = this.files.value[index];
				const file = new Blob([await doc.arrayBuffer()], {
					type: "application/octet-stream",
				});
				files.push(file);
			}
			this._rawField.value = files.map((el, index) => ({
				name: this.files.value[index].name,
				href: "",
				file: el,
			}));
		});
	}

	public get rawValue(): Array<DocumentSchema> {
		return this._rawField.value;
	}
}

class EnumSmartField extends InputSmartField {
	protected readonly _delay: number = 50;

	constructor(
		name: string,
		fieldName: string,
		protected list: Array<string>,
		defaultValue?: any,
		canEdit: boolean = true,
		formatter?: (value: any) => string,
		public readonly required: boolean = false,
	) {
		super(name, fieldName, defaultValue, canEdit, required, false);
		this._tipList.value = this.list;

		if (formatter) {
			this.formatter = formatter;
		}
	}

	protected formatter(value: any): string {
		return value;
	}
	protected tipFormatter(value: any): string {
		return this.formatter(value);
	}
	protected async setter(newValue: any): Promise<void> {
		if (newValue.length === 0) {
			this._tipList.value = this.list;
			return;
		}

		this._tipList.value = this.list.filter(
			(val) =>
				this.formatter(val).toLowerCase().indexOf(newValue.toLowerCase()) !==
				-1,
		);
	}
}

class BoolSmartField extends EnumSmartField {
	constructor(
		name: string,
		fieldName: string,
		defaultValue?: any,
		canEdit: boolean = true,
		public readonly required: boolean = false,
	) {
		super(
			name,
			fieldName,
			["Да", "Нет"],
			defaultValue,
			canEdit,
			undefined,
			required,
		);
	}

	public get rawValue(): boolean {
		return this._rawField.value === "Да";
	}
}

class DateTimeSmartField extends InputSmartField {
	constructor(
		name: string,
		fieldName: string,
		defaultValue?: any,
		canEdit: boolean = true,
		public readonly required: boolean = false,
		public mode: string = "datetime",
	) {
		super(name, fieldName, defaultValue, canEdit, required, false);
	}

	protected formatter(value: any): string {
		if (this.mode === "datetime") {
			return parser.formatDateTime(value).toString();
		} else {
			return parser.formatDate(value).toString();
		}
	}
	protected async setter(newValue: any): Promise<void> {
		if (newValue === "") {
			this._rawField.value = null;
			return;
		}

		this._rawField.value = newValue;

		const date: any = new Date(newValue);
		if (date instanceof Date && !isNaN(date.getDate())) {
			this.completed.value = true;
		} else {
			this.completed.value = false;
		}
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
			new WorkerSmartField("Работник", "worker", _instance?.worker, true, true),
			new DepartmentSmartField(
				"Производство",
				"department",
				_instance?.department,
				true,
				true,
			),
			new PostSmartField("Должность", "post", _instance?.post, true, true),
			new DateTimeSmartField(
				"Начало смены",
				"work_begin",
				_instance?.work_begin,
				true,
				true,
			),
			new DateTimeSmartField("Конец смены", "work_end", _instance?.work_end),
			new DateTimeSmartField("День", "day", _instance?.day, true, true, "date"),
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
			new InputSmartField("Cумма", "amount", undefined, true, true),
			new EnumSmartField(
				"Тип оплаты",
				"payment_type",
				["cash", "card", "taxi"],
				undefined,
				true,
				(val) => {
					switch (val) {
						case "cash":
							return "Наличная";
						case "card":
							return "Безналичная";
						case "taxi":
							return "Требуется такси";
					}
					return val;
				},
				true,
			),
			new ExpenditureSmartField(
				"Статья",
				"expenditure",
				undefined,
				true,
				undefined,
				true,
			),
			new BoolSmartField("Счет в ЭДО", "need_edm", "Нет"),
			new DepartmentSmartField(
				"Производство",
				"department",
				undefined,
				true,
				true,
			),
			new InputSmartField("Цель", "purpose", undefined, true, true),
			new DocumentSmartField("Документы", "documents", undefined, true),
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
		public readonly required: boolean = false,
	) {
		super(name, fieldName, defaultValue, canEdit, required, false);
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

export class ExpenditureSmartField extends InputSmartField {
	private _endpoint: string = "";
	protected readonly _delay: number = 200;

	constructor(
		name: string,
		fieldName: string,
		defaultValue?: any,
		canEdit: boolean = true,
		protected chapterField?: InputSmartField,
		public readonly required: boolean = false,
	) {
		super(name, fieldName, defaultValue, canEdit, required, false);
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
		public readonly required: boolean = false,
	) {
		super(name, fieldName, defaultValue, canEdit, required, false);
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
		public readonly required: boolean = false,
	) {
		super(name, fieldName, defaultValue, canEdit, required, false);
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
//#endregion
