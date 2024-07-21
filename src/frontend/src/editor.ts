import { computed, Ref, ref } from "vue";

export class SmartField {
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

	protected _formatter: (value: any) => string = (value) => `${value}`;
	protected _setter: (newValue: any) => void = (newValue: any) =>
		(this._rawField.value = newValue);

	public formattedField = computed({
		get: () => {
			return this._formatter(this._rawField.value);
		},
		set: (newValue: string) => {
			this._setter(newValue);
		},
	});

	public get rawValue() {
		return this._rawField.value;
	}

	public selectList = computed(() => {
		return this._tipList.value.map((value) => this._formatter(value));
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
			];
		}
	}
}
