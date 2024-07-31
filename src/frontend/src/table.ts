import { computed, ref, Ref } from "vue";
import * as config from "@/config";
import * as parser from "@/parser";
import axios from "axios";
import {
	BaseSchema,
	BidSchema,
	BudgetSchema,
	ExpenditureSchema,
} from "./types";
import { useNetworkStore } from "./store/network";

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

export class Cell {
	public cellLines: Array<CellLine> = [];

	constructor(...cellLines: Array<CellLine>) {
		if (cellLines.length === 0) {
			cellLines.push(new CellLine());
		}
		this.cellLines = cellLines;
	}

	public toString(): string {
		return this.cellLines.map((cellLine) => cellLine.value).join();
	}
}

export class CellLine {
	constructor(
		public value: string = "Не указано",
		public href: string = "",
		public color: string = "",
	) {}
}

export class Table<T extends BaseSchema> {
	private _highlighted: Ref<Array<boolean>> = ref([]);
	private _checked: Ref<Array<boolean>> = ref([]);
	/**  Key - ID, Value - index in internal arrays. */
	protected _indexes: Map<number, number> = new Map();
	protected _models: Ref<Array<T>> = ref([]);
	private _endpoint: string = "";
	private _network = useNetworkStore();

	/**
	 * @param tableContent
	 * @param _searchFields Indexes of columns for searching.
	 */
	constructor(modelName: string) {
		this._endpoint = `${config.fullBackendURL}/${config.crmEndpoint}/${modelName}`;
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
		const result: Array<{ id: number; columns: Array<Cell> }> = [];

		for (let index = 0; index < this._filteredRows.value.length; index++) {
			const model = this._filteredRows.value[index];
			const columns: Array<Cell> = [];

			for (const fieldName in model) {
				const field = model[fieldName];
				const formatter = this.getFormatter(fieldName);

				const formattedField: Cell = formatter(field);

				const index = this._columsOrder.get(fieldName);

				if (index && columns.length > index) {
					columns.splice(index, 0, formattedField);
				} else {
					columns.push(formattedField);
				}
			}

			result.push({ id: model.id, columns: columns });
		}

		return result;
	});
	public rows = computed(() => {
		if (this.isHidden.value) {
			return [];
		}

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

			const index = this._columsOrder.get(fieldName);

			if (index && result.length > index) {
				result.splice(index, 0, alias);
			} else {
				result.push(alias);
			}
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
	/** Default forrmatter for column value */
	protected _defaultFormatter: (value: any) => Cell = (value: any): Cell => {
		if (value === null) {
			return new Cell();
		} else {
			return new Cell(new CellLine(`${value}`));
		}
	};
	/** Formatters for column values */
	protected _formatters: Map<string, (value: any) => Cell> = new Map<
		string,
		(value: any) => Cell
	>();
	private getFormatter(fieldName: string): (value: any) => Cell {
		const formatter = this._formatters.get(fieldName);

		if (formatter) {
			return formatter;
		} else {
			return this._defaultFormatter;
		}
	}
	/** Order of column in table */
	protected _columsOrder: Map<string, number> = new Map<string, number>();
	/** Aliases for column names */
	protected _aliases: Map<string, string> = new Map<string, string>();
	/** Filters for rows. Must returns **true** if row need be shown. */
	public filters: Ref<Array<(model: any) => boolean>> = ref([]);
	/** Searcher for rows. Must returns **true** if row need be shown. */
	public searcher: Ref<(model: any) => boolean> = ref((_) => true);
	/** True when table is execute large loading operations. */
	public isLoading: Ref<boolean> = ref(false);
	/** Hides all row if true */
	public isHidden: Ref<boolean> = ref(false);
	/** Emulates loading by hidding table rows and setting **this.isLoading** to **true** if **value** = **true** */
	public emulateLoading(value: boolean) {
		this.isLoading.value = value;
		this.isHidden.value = value;
	}
	public highlightedCount = computed(() => {
		let result = 0;
		for (const elemHighlighted of this._highlighted.value) {
			if (elemHighlighted) {
				result++;
			}
		}
		return result;
	});
	/** Erases row after approving or rejecting if true. */
	protected _deleteAfterStatusChanged: boolean = false;
	//#endregion

	//#region CRUD
	public push(model: T, highlighted: boolean = false): void {
		this._indexes.set(model.id, this._models.value.length);
		this._models.value.push(model);
		this._checked.value.push(false);
		this._highlighted.value.push(highlighted);
	}
	public async loadAll(silent: boolean = false): Promise<number> {
		this.isLoading.value = true && !silent;
		let changesCount = 0;
		const resp = await this._network.withAuthChecking(
			axios.get(this._endpoint + "/"),
		);
		this.isLoading.value = false;
		const models = resp.data;
		for (let i = 0; i < models.length; i++) {
			const model: T = models[i];

			let modelFounded = false;
			for (let j = 0; j < this._models.value.length; j++) {
				const oldModel = this._models.value[j];

				if (oldModel.id !== model.id) {
					continue;
				}

				modelFounded = true;

				// Changes fields in model which was changed in new model.
				for (const fieldName in model) {
					const formatter = this.getFormatter(fieldName);

					const modelString: string = formatter(model[fieldName]).toString();
					const oldModelString: string = formatter(
						oldModel[fieldName],
					).toString();

					if (modelString !== oldModelString) {
						changesCount++;
						for (const fieldName in model) {
							this._models.value[j][fieldName] = model[fieldName];
						}
						this._highlighted.value[j] = true;
						break;
					}
				}
				break;
			}

			if (!modelFounded) {
				changesCount++;
				this.push(model, silent);
			}
		}

		return changesCount;
	}
	public async create(model: T): Promise<void> {
		await this._network.withAuthChecking(
			axios.post(`${this._endpoint}/`, model),
		);

		const resp = await this._network.withAuthChecking(
			axios.get(`${this._endpoint}/last`),
		);
		this.push(resp.data, false);
	}
	public async update(model: T, id: number): Promise<void> {
		const index = this._indexes.get(id);
		if (index === undefined) throw new Error(`ID ${id} not exist`);
		let elementChanged = false;
		for (const fieldName in model) {
			const formatter = this.getFormatter(fieldName);

			const modelString: string = formatter(model[fieldName]).toString();
			const oldModelString: string = formatter(
				this._models.value[index][fieldName],
			).toString();

			if (modelString !== oldModelString) {
				elementChanged = true;
			}
			this._models.value[index][fieldName] = model[fieldName];
		}

		if (elementChanged) {
			await this._network.withAuthChecking(
				axios.patch(`${this._endpoint}/`, this._models.value[index]),
			);
		}
	}
	public async delete(id: number): Promise<void> {
		const deleteIndex = this._indexes.get(id)!;
		if (deleteIndex === undefined) throw new Error(`ID ${id} not exist`);
		await this._network.withAuthChecking(
			axios.delete(`${this._endpoint}/${this._models.value[deleteIndex].id}`),
		);
	}
	public async erase(id: number): Promise<void> {
		const deleteIndex = this._indexes.get(id);
		if (deleteIndex === undefined) throw new Error(`ID ${id} not exist`);
		this._indexes.delete(id);

		this._checked.value.splice(deleteIndex, 1);
		this._highlighted.value.splice(deleteIndex, 1);
		this._models.value.splice(deleteIndex, 1);
		for (let index = deleteIndex; index < this._models.value.length; index++) {
			const model = this._models.value[index];
			this._indexes.set(model.id, this._indexes.get(model.id)! - 1);
		}
	}
	public async deleteChecked(): Promise<void> {
		this.emulateLoading(true);
		for (let index = 0; index < this._models.value.length; index++) {
			const id = this._models.value[index].id;

			if (this._checked.value[index]) {
				await this.delete(id);
				await this.erase(id);
				index--;
			}
		}
		this.emulateLoading(false);
	}
	public getModel(id: number): any {
		const index = this._indexes.get(id);
		if (index === undefined) throw new Error(`ID ${id} not exist`);

		return this._models.value[index];
	}
	public async approve(id: number): Promise<void> {
		const approveIndex = this._indexes.get(id)!;

		await this._network.withAuthChecking(
			axios.patch(
				`${this._endpoint}/approve/${this._models.value[approveIndex].id}`,
			),
		);

		if (this._deleteAfterStatusChanged) {
			this.erase(id);
		}
	}
	public async approveChecked(): Promise<void> {
		this.emulateLoading(true);
		for (let index = 0; index < this._models.value.length; index++) {
			const id = this._models.value[index].id;

			if (this._checked.value[index]) {
				await this.approve(id);
			}
		}
		this.allChecked.value = false;
		this.emulateLoading(false);
	}
	public async reject(id: number): Promise<void> {
		const approveIndex = this._indexes.get(id)!;

		await this._network.withAuthChecking(
			axios.patch(
				`${this._endpoint}/reject/${this._models.value[approveIndex].id}`,
			),
		);

		if (this._deleteAfterStatusChanged) {
			this.erase(id);
		}
	}
	public async rejectChecked(): Promise<void> {
		this.emulateLoading(true);
		for (let index = 0; index < this._models.value.length; index++) {
			const id = this._models.value[index].id;

			if (this._checked.value[index]) {
				await this.reject(id);
			}
		}
		this.allChecked.value = false;
		this.emulateLoading(false);
	}
	//#endregion
}

//#region Panel tables
export class ExpenditureTable extends Table<ExpenditureSchema> {
	constructor() {
		super("expenditure");

		this._formatters.set("fac", parser.formatWorker);
		this._formatters.set("cc", parser.formatWorker);
		this._formatters.set("cc_supervisor", parser.formatWorker);
		this._formatters.set("creator", parser.formatWorker);
		this._formatters.set("create_date", parser.formatDate);

		this._aliases.set("id", "ID");
		this._aliases.set("name", "Статья");
		this._aliases.set("chapter", "Раздел");
		this._aliases.set("create_date", "Дата создания");
		this._aliases.set("fac", "ЦФО");
		this._aliases.set("cc", "ЦЗ");
		this._aliases.set("cc_supervisor", "Руководитель ЦЗ");
		this._aliases.set("creator", "Создал");
	}
}

export class BudgetTable extends Table<BudgetSchema> {
	constructor() {
		super("budget");

		this._formatters.set("expenditure", parser.formatExpenditure);
		this._formatters.set("department", parser.formatDepartment);

		this._aliases.set("id", "ID");
		this._aliases.set("limit", "Лимит");
		this._aliases.set("expenditure", "Статья");
		this._aliases.set("last_update", "Последние обновление");
		this._aliases.set("department", "Производство");
		this._aliases.set("chapter", "Раздел");

		this._columsOrder.set("id", 0);
		this._columsOrder.set("chapter", 1);
		this._columsOrder.set("expenditure", 2);
	}
}

export class BidTable extends Table<BidSchema> {
	constructor() {
		super("bid");

		this._formatters.set("department", parser.formatDepartment);
		this._formatters.set("worker", parser.formatWorker);
		this._formatters.set("create_date", parser.formatDate);
		this._formatters.set("close_date", parser.formatDate);
		this._formatters.set("documents", parser.formatDocuments);
		this._formatters.set("payment_type", parser.formatPaymentType);

		this._aliases.set("id", "ID");
		this._aliases.set("amount", "Сумма");
		this._aliases.set("payment_type", "Тип оплаты");
		this._aliases.set("department", "Произовдство");
		this._aliases.set("worker", "Работник");
		this._aliases.set("purpose", "Цель");
		this._aliases.set("create_date", "Дата создания");
		this._aliases.set("close_date", "Дата закрытия");
		this._aliases.set("status", "Статус");
		this._aliases.set("comment", "Комментарий");
		this._aliases.set("documents", "Документы");

		this._columsOrder.set("id", 0);
		this._columsOrder.set("create_date", 1);
		this._columsOrder.set("close_date", 2);
		this._columsOrder.set("worker", 3);
		this._columsOrder.set("amount", 4);
		this._columsOrder.set("documents", 5);
		this._columsOrder.set("payment_type", 6);
		this._columsOrder.set("department", 7);
		this._columsOrder.set("purpose", 8);
		this._columsOrder.set("status", 9);
		this._columsOrder.set("comment", 10);
	}
}
//#endregion
