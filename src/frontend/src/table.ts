import { computed, ref, Ref } from "vue";
import * as config from "@/config";
import * as parser from "@/parser";
import axios from "axios";

class TableElementObserver<T> {
	constructor(
		private _element: T,
		private _elementID: number,
		private _callback: (elementID: number, newValue: T) => void,
	) {}

	get value() {
		return this._element;
	}

	set value(newValue: T) {
		this._element = newValue;
		this._callback(this._elementID, newValue);
	}
}

export class Table {
	private _highlighted: Array<boolean> = [];
	private _checked: Array<boolean> = [];
	/**  Key - ID, Value - index in internal arrays. */
	protected _indexes: Map<number, number> = new Map();
	private _nextKey: number = 0;
	protected _models: Ref<Array<{ key: number; instance: any }>> = ref([]);

	private _endpoint: string = "";

	/**
	 * @param tableContent
	 * @param _searchFields Indexes of columns for searching.
	 */
	constructor(tableContent: Array<Array<string>>, tableName: string) {
		this._endpoint = `http://${config.backendDomain}:${config.backendPort}/${config.crmEndpoint}/panel/${tableName}`;

		for (let index = 0; index < tableContent.length; index++) {
			const row = tableContent[index];
			this.push(row);
		}
	}

	private clear(): void {
		this._highlighted = [];
		this._checked = [];
		this._indexes.clear();
		this._nextKey = 0;
		this._models.value = [];
	}

	private elementUpdated(key: number): void {
		const curIndex = this._indexes.get(key);
		if (curIndex === undefined) throw new Error(`Key ${key} not exist`);

		this._models.value[curIndex].key = this._nextKey;
		this._indexes.delete(key);
		this._indexes.set(this._nextKey, curIndex);
		this._nextKey++;
	}

	private elementChecked(key: number, newValue: boolean): void {
		const curIndex = this._indexes.get(key);
		if (curIndex === undefined) throw new Error(`Key ${key} not exist`);

		this._checked[curIndex] = newValue;
		this.elementUpdated(key);
	}
	private elementHighlighted(key: number, newValue: boolean): void {
		const curIndex = this._indexes.get(key);
		if (curIndex === undefined) throw new Error(`Key ${key} not exist`);

		this._highlighted[curIndex] = newValue;
		this.elementUpdated(key);
	}

	private _searchedRows = computed(() => {
		const searchResult: Array<{ key: number; instance: any }> = [];
		for (let index = 0; index < this._models.value.length; index++) {
			const model = this._models.value[index];
			if (this.searcher.value(model.instance)) {
				searchResult.push(model);
			}
		}
		return searchResult;
	});

	private _filteredRows = computed(() => {
		const filterResult: Array<{ key: number; instance: any }> =
			this._searchedRows.value.filter(
				(model: { key: number; instance: any }) => {
					for (const filter of this.filters.value) {
						if (!filter(model.instance)) return false;
					}
					return true;
				},
			);

		return filterResult;
	});

	private _formattedRows = computed(() => {
		const result: Array<{ key: number; columns: Array<string> }> = [];

		for (let index = 0; index < this._filteredRows.value.length; index++) {
			const model = this._filteredRows.value[index];
			const columns: Array<string> = [];

			for (const fieldKey in model.instance) {
				const field = model.instance[fieldKey];
				const formatter = this._formatters.get(fieldKey);

				if (formatter) {
					columns.push(formatter(field));
				} else {
					columns.push(`${field}`);
				}
			}

			result.push({ key: model.key, columns });
		}

		return result;
	});

	// Protected fields
	protected _formatters: Map<string, (value: any) => string> = new Map<
		string,
		(value: any) => string
	>();

	public isLoading: Ref<boolean> = ref(false);
	/** Filters for rows. Must returns **true** if row need be shown. */
	public filters: Ref<Array<(instance: any) => boolean>> = ref([]);
	/** Searcher for rows. Must returns **true** if row need be shown. */
	public searcher: Ref<(instance: any) => boolean> = ref((_) => true);

	public data = computed(() => {
		return this._formattedRows.value;
	});

	public getInstance(key: number): any {
		const index = this._indexes.get(key);
		if (index === undefined) throw new Error(`Key ${key} not exist`);

		return this._models.value[index].instance;
	}

	public async loadAll() {
		this.isLoading.value = true;
		const resp = await axios.get(`${this._endpoint}s`);
		this.isLoading.value = false;
		const models = resp.data.dumps;
		for (let index = 0; index < models.length; index++) {
			const model = models[index];
			this.push(model);
		}
	}

	public async create(instance: any) {
		await axios.post(`${this._endpoint}/create`, instance);

		this.clear();
		await this.loadAll();
		this._highlighted[this._highlighted.length - 1] = true;
	}

	public async update(instance: any, key: number) {
		const index = this._indexes.get(key);
		if (index === undefined) throw new Error(`Key ${key} not exist`);
		for (const fieldName in instance) {
			this._models.value[index].instance[fieldName] = instance[fieldName];
		}

		await axios.patch(
			`${this._endpoint}/update`,
			this._models.value[index].instance,
		);
		this.elementUpdated(key);
	}

	public isChecked(key: number): TableElementObserver<boolean> {
		return new TableElementObserver(
			this._checked[this._indexes.get(key)!],
			key,
			this.elementChecked.bind(this),
		);
	}

	public isHighlighted(key: number): TableElementObserver<boolean> {
		return new TableElementObserver(
			this._highlighted[this._indexes.get(key)!],
			key,
			this.elementHighlighted.bind(this),
		);
	}

	public isAnyChecked(): boolean {
		for (let index = 0; index < this._checked.length; index++) {
			if (this._checked[index]) return true;
		}
		return false;
	}

	public push(model: any): void {
		this._models.value.push({ instance: model, key: this._nextKey });
		this._indexes.set(this._nextKey, this._checked.length);
		this._checked.push(false);
		this._highlighted.push(false);
		this._nextKey++;
	}

	public async erase(key: number): Promise<void> {
		const deleteIndex = this._indexes.get(key)!;
		if (!this._indexes.delete(key)) throw new Error(`Key ${key} not exist`);

		await axios.delete(
			`${this._endpoint}/delete?rowID=${this._models.value[deleteIndex].instance.id}`,
		);

		this._checked.splice(deleteIndex, 1);
		this._highlighted.splice(deleteIndex, 1);
		this._models.value.splice(deleteIndex, 1);
		for (let index = deleteIndex; index < this._models.value.length; index++) {
			const element = this._models.value[index];
			this._indexes.set(element.key, this._indexes.get(element.key)! - 1);
		}
	}

	public async deleteChecked(): Promise<void> {
		for (let index = 0; index < this._models.value.length; index++) {
			const key = this._models.value[index].key;

			if (this._checked[index]) {
				await this.erase(key);
				index--;
			}
		}
	}
}

export class ExpenditureTable extends Table {
	constructor(tableContent: Array<Array<string>>, tableName: string) {
		super(tableContent, tableName);

		this._formatters.set("fac", parser.formatWorker);
		this._formatters.set("cc", parser.formatWorker);
		this._formatters.set("cc_supervisor", parser.formatWorker);
		this._formatters.set("create_date", parser.formatDate);
	}
}
