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
	 * @param _searchColumnIndexes Indexes of columns for searching.
	 */
	constructor(
		tableContent: Array<Array<string>>,
		tableName: string,
		private _searchColumnIndexes: Array<number> = [],
	) {
		this._endpoint = `http://${config.backendDomain}:${config.backendPort}/${config.crmEndpoint}/panel/${tableName}`;

		for (let index = 0; index < tableContent.length; index++) {
			const row = tableContent[index];
			this.push(row);
		}
	}

	private elementChecked(key: number, newValue: boolean): void {
		const curIndex = this._indexes.get(key)!;
		this._checked[curIndex] = newValue;
		this._models.value[curIndex].key = this._nextKey;
		this._indexes.delete(key);
		this._indexes.set(this._nextKey, curIndex);
		this._nextKey++;
	}
	private elementHighlighted(key: number, newValue: boolean): void {
		const curIndex = this._indexes.get(key)!;
		this._highlighted[curIndex] = newValue;
		this._models.value[curIndex].key = this._nextKey;
		this._indexes.delete(key);
		this._indexes.set(this._nextKey, curIndex);
		this._nextKey++;
	}

	private _formattedRows = computed(
		(): Array<{ key: number; columns: Array<string> }> => {
			const result: Array<{ key: number; columns: Array<string> }> = [];

			for (let index = 0; index < this._models.value.length; index++) {
				const model = this._models.value[index];
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
		},
	);

	private _searchedRows = computed(() => {
		const searchResult: Array<{ key: number; columns: Array<string> }> = [];

		for (let index = 0; index < this._formattedRows.value.length; index++) {
			const row = this._formattedRows.value[index];

			for (const columnIndex of this._searchColumnIndexes) {
				if (columnIndex >= row.columns.length) {
					break;
				}
				const searchString = this.searchString.value.toLowerCase();
				const talbeElement = row.columns[columnIndex].toLowerCase();
				if (talbeElement.indexOf(searchString) !== -1) {
					searchResult.push(row);
					break;
				}
			}
		}

		return searchResult;
	});

	private _filteredRows = computed(() => {
		const filterResult: Array<{ key: number; columns: Array<string> }> =
			this._searchedRows.value.filter(
				(row: { key: number; columns: Array<string> }) => {
					for (const filter of this.filters.value) {
						if (!filter(row)) return false;
					}
					return true;
				},
			);

		return filterResult;
	});

	// Protected fields
	protected _formatters: Map<string, (value: any) => string> = new Map<
		string,
		(value: any) => string
	>();

	// Public fields
	public searchString: Ref<string> = ref("");
	/** Filters for rows. Must returns **true** if row need be shown. */
	public filters: Ref<
		Array<(row: { key: number; columns: Array<string> }) => boolean>
	> = ref([]);

	public data = computed(() => {
		return this._filteredRows.value;
	});

	public async load() {
		const resp = await axios.get(`${this._endpoint}s`);
		if (resp.status < 400) {
			const models = resp.data.dumps;
			for (let index = 0; index < models.length; index++) {
				const model = models[index];
				this.push(model);
			}
		}
	}

	public cloneRow(key: number): Array<string> {
		const index = this._indexes.get(key);
		if (index === undefined) throw new Error(`Key ${key} not exist`);

		const result: Array<string> = [];

		for (const elem of this._formattedRows.value[index].columns) {
			result.push(elem.slice());
		}

		return result;
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

	public erase(key: number): void {
		const deleteIndex = this._indexes.get(key)!;
		if (!this._indexes.delete(key)) throw new Error(`Key ${key} not exist`);
		this._checked.splice(deleteIndex, 1);
		this._highlighted.splice(deleteIndex, 1);
		this._models.value.splice(deleteIndex, 1);
		for (let index = deleteIndex; index < this._models.value.length; index++) {
			const element = this._models.value[index];
			this._indexes.set(element.key, this._indexes.get(element.key)! - 1);
		}
	}

	public deleteChecked(): void {
		for (let index = 0; index < this._models.value.length; index++) {
			const key = this._models.value[index].key;

			if (this._checked[index]) {
				this.erase(key);
				index--;
			}
		}
	}
}

export class ExpenditureTable extends Table {
	constructor(
		tableContent: Array<Array<string>>,
		tableName: string,
		searchColumnIndexes: Array<number> = [],
	) {
		super(tableContent, tableName, searchColumnIndexes);

		this._formatters.set("fac", parser.formatWorker);
		this._formatters.set("cc", parser.formatWorker);
		this._formatters.set("cc_supervisor", parser.formatWorker);
		this._formatters.set("create_date", parser.formatDate);
	}
}
