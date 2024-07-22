import { computed, ref, Ref } from "vue";
import * as config from "@/config";
import * as parser from "@/parser";
import axios from "axios";
import { BaseSchema, ExpenditureSchema } from "./types";

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

export class Table<T extends BaseSchema> {
	private _highlighted: Ref<Array<boolean>> = ref([]);
	private _checked: Ref<Array<boolean>> = ref([]);
	/**  Key - ID, Value - index in internal arrays. */
	protected _indexes: Map<number, number> = new Map();
	protected _models: Ref<Array<T>> = ref([]);
	private _endpoint: string = "";

	/**
	 * @param tableContent
	 * @param _searchFields Indexes of columns for searching.
	 */
	constructor(tableName: string) {
		this._endpoint = `${config.fullBackendURL}/${config.crmEndpoint}/panel/${tableName}`;
	}

	//#region Rows handlers
	private _searchedRows = computed(() => {
		const searchResult: Array<T> = [];
		for (let index = 0; index < this._models.value.length; index++) {
			const model = this._models.value[index];
			if (this.searcher.value(model)) {
				searchResult.push(model);
			}
		}
		return searchResult;
	});
	private _filteredRows = computed(() => {
		const filterResult: Array<T> = this._searchedRows.value.filter(
			(model: T) => {
				for (const filter of this.filters.value) {
					if (!filter(model)) return false;
				}
				return true;
			},
		);

		return filterResult;
	});
	private _formattedRows = computed(() => {
		const result: Array<{ id: number; columns: Array<string> }> = [];

		for (let index = 0; index < this._filteredRows.value.length; index++) {
			const model = this._filteredRows.value[index];
			const columns: Array<string> = [];

			for (const fieldName in model) {
				const field = model[fieldName];
				const formatter = this._formatters.get(fieldName);

				if (formatter) {
					columns.push(formatter(field));
				} else {
					columns.push(`${field}`);
				}
			}

			result.push({ id: model.id, columns: columns });
		}

		return result;
	});
	public rows = computed(() => {
		return this._formattedRows.value;
	});
	public headers = computed(() => {
		const result: Array<string> = [];
		if (this._models.value.length === 0) return result;

		for (const fieldName in this._models.value[0]) {
			let alias = this._aliases.get(fieldName);
			if (alias === undefined) {
				alias = fieldName;
			}
			result.push(alias);
		}
		return result;
	});
	public allChecked = computed({
		get: () => {
			if (this._checked.value.length === 0) {
				return false;
			}
			for (let index = 0; index < this._checked.value.length; index++) {
				if (!this._checked.value[index]) {
					return false;
				}
			}
			return true;
		},
		set: (newValue: boolean) => {
			for (let index = 0; index < this._checked.value.length; index++) {
				this._checked.value[index] = newValue;
			}
		},
	});
	public anyChecked = computed(() => {
		for (let index = 0; index < this._checked.value.length; index++) {
			if (this._checked.value[index]) {
				return true;
			}
		}
		return false;
	});
	private _elementChecked(id: number, newValue: boolean) {
		const index = this._indexes.get(id)!;

		this._checked.value[index] = newValue;
	}
	public checked = computed(() => {
		const result: Map<number, TableElementObserver<boolean>> = new Map<
			number,
			TableElementObserver<boolean>
		>();
		for (let index = 0; index < this._models.value.length; index++) {
			const modelID = this._models.value[index].id;

			result.set(
				modelID,
				new TableElementObserver(
					this._checked.value[this._indexes.get(modelID)!],
					modelID,
					this._elementChecked.bind(this),
				),
			);
		}

		return result;
	});
	private _elementHighlighted(id: number, newValue: boolean) {
		const index = this._indexes.get(id)!;

		this._highlighted.value[index] = newValue;
	}
	public highlighted = computed(() => {
		const result: Map<number, TableElementObserver<boolean>> = new Map<
			number,
			TableElementObserver<boolean>
		>();

		for (let index = 0; index < this._models.value.length; index++) {
			const modelID = this._models.value[index].id;

			result.set(
				modelID,
				new TableElementObserver(
					this._highlighted.value[this._indexes.get(modelID)!],
					modelID,
					this._elementHighlighted.bind(this),
				),
			);
		}

		return result;
	});
	//#endregion

	//#region Auxiliary fields
	/** Formatters for column values */
	protected _formatters: Map<string, (value: any) => string> = new Map<
		string,
		(value: any) => string
	>();
	/** Aliases for column names */
	protected _aliases: Map<string, string> = new Map<string, string>();
	/** Filters for rows. Must returns **true** if row need be shown. */
	public filters: Ref<Array<(instance: any) => boolean>> = ref([]);
	/** Searcher for rows. Must returns **true** if row need be shown. */
	public searcher: Ref<(instance: any) => boolean> = ref((_) => true);
	public isLoading: Ref<boolean> = ref(false);
	//#endregion

	//#region CRUD
	public push(model: T): void {
		this._indexes.set(model.id, this._models.value.length);
		this._models.value.push(model);
		this._checked.value.push(false);
	}
	public async loadAll(silent: boolean = false) {
		this.isLoading.value = true && !silent;
		const resp = await axios.get(`${this._endpoint}s`);
		this.isLoading.value = false;
		const models = resp.data.dumps;
		for (let index = 0; index < models.length; index++) {
			const model: T = models[index];

			let modelFounded = false;
			for (const oldModel of this._models.value) {
				if (oldModel.id === model.id) {
					modelFounded = true;
					break;
				}
			}

			if (!modelFounded) {
				this.push(model);
			}
		}
	}
	public async create(instance: T) {
		await axios.post(`${this._endpoint}/create`, instance);

		const resp = await axios.get(`${this._endpoint}/last`);
		this.push(resp.data);
		this._highlighted.value[this._indexes.get(resp.data.id)!] = true;
	}
	public async update(instance: T, id: number) {
		const index = this._indexes.get(id);
		if (index === undefined) throw new Error(`ID ${id} not exist`);
		for (const fieldName in instance) {
			this._models.value[index][fieldName] = instance[fieldName];
		}

		await axios.patch(`${this._endpoint}/update`, this._models.value[index]);
	}
	public async erase(id: number): Promise<void> {
		const deleteIndex = this._indexes.get(id)!;
		if (!this._indexes.delete(id)) throw new Error(`ID ${id} not exist`);

		await axios.delete(
			`${this._endpoint}/delete?rowID=${this._models.value[deleteIndex].id}`,
		);

		this._checked.value.splice(deleteIndex, 1);
		this._highlighted.value.splice(deleteIndex, 1);
		this._models.value.splice(deleteIndex, 1);
		for (let index = deleteIndex; index < this._models.value.length; index++) {
			const model = this._models.value[index];
			this._indexes.set(model.id, this._indexes.get(model.id)! - 1);
		}
	}
	public async deleteChecked(): Promise<void> {
		for (let index = 0; index < this._models.value.length; index++) {
			const id = this._models.value[index].id;

			if (this._checked.value[index]) {
				await this.erase(id);
				index--;
			}
		}
	}
	public getModel(id: number): any {
		const index = this._indexes.get(id);
		if (index === undefined) throw new Error(`ID ${id} not exist`);

		return this._models.value[index];
	}
	//#endregion
}

export class ExpenditureTable extends Table<ExpenditureSchema> {
	constructor(tableName: string) {
		super(tableName);

		this._formatters.set("fac", parser.formatWorker);
		this._formatters.set("cc", parser.formatWorker);
		this._formatters.set("cc_supervisor", parser.formatWorker);
		this._formatters.set("create_date", parser.formatDate);

		this._aliases.set("id", "ID");
		this._aliases.set("name", "Статья");
		this._aliases.set("chapter", "Раздел");
		this._aliases.set("create_date", "Дата создания");
		this._aliases.set("limit", "Лимит");
		this._aliases.set("fac", "ЦФО");
		this._aliases.set("cc", "ЦЗ");
		this._aliases.set("cc_supervisor", "Руководитель ЦЗ");
	}
}
