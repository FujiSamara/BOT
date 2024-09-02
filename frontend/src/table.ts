import { computed, ref, Ref, watch } from "vue";
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

/** Presents class for external usage. */
interface TableData {
	rows: Array<{ id: number; columns: Array<Cell> }>;
	headers: Array<string>;
}

interface OrderBySchema {
	column: string;
	desc: boolean;
}

interface SearchSchema {
	column: string;
	term: string;
	dependencies?: Array<SearchSchema>;
	groups?: Array<number>;
}

interface DateSchema {
	column: string;
	start: Date;
	end: Date;
}

interface FilterSchema {
	column: string;
	value: string;
}

interface QuerySchema {
	search_query?: Array<SearchSchema>;
	order_by_query?: OrderBySchema;
	date_query?: DateSchema;
	filter_query?: Array<FilterSchema>;
}

export class Table<T extends BaseSchema> {
	private _highlighted: Ref<Array<boolean>> = ref([]);
	private _checked: Ref<Array<boolean>> = ref([]);
	private _loadedRows: Ref<Array<T>> = ref([]);
	private _network = useNetworkStore();
	private _refreshKey: Ref<number> = ref(0);
	private _newIds: Ref<Array<number>> = ref([]);

	/**
	 * @param endpoint Endpoint name for api.
	 */
	constructor(
		endpoint: string,
		options?: {
			getEndpoint?: string;
			infoEndpoint?: string;
			createEndpoint?: string;
			updateEndpoint?: string;
			deleteEndpoint?: string;
			approveEndpoint?: string;
			rejectEndpoint?: string;
		},
	) {
		this._endpoint = `${config.fullBackendURL}/${config.crmEndpoint}/${endpoint}`;

		//#region endpoints
		this._getEndpoint =
			options && options.getEndpoint ? options.getEndpoint : "";
		this._infoEndpoint =
			options && options.infoEndpoint ? options.infoEndpoint : "";
		this._createEndpoint =
			options && options.createEndpoint ? options.createEndpoint : "";
		this._updateEndpoint =
			options && options.updateEndpoint ? options.updateEndpoint : "";
		this._deleteEndpoint =
			options && options.deleteEndpoint ? options.deleteEndpoint : "";
		this._approveEndpoint =
			options && options.approveEndpoint ? options.approveEndpoint : "";
		this._rejectEndpoint =
			options && options.rejectEndpoint ? options.rejectEndpoint : "";
		//#endregion

		this.startUpdatingLoop();
	}

	//#region Rows
	//#region Refreshing
	private async startUpdatingLoop() {
		let skipLoop = false;

		watch(
			[this._completedQuery, this._rowsQuery, this._refreshKey],
			async () => {
				this.emulateLoading(true);
				skipLoop = true;
				await this.refreshInfo();
				await this.refreshRows();
				this.emulateLoading(false);
			},
		);

		const loop = async () => {
			if (!skipLoop) {
				await this.refreshInfo(true);
			}
			skipLoop = false;

			setTimeout(async () => await loop(), this.updateTimeout * 1000);
		};

		setTimeout(async () => await loop(), this.updateTimeout * 1000);
	}
	/** Updates info about table:
	 * 1) Page count
	 * 2) Row count
	 *
	 * - If **fromLoop** is **true** and row count changed then force refreshes rows.
	 */
	private async refreshInfo(fromLoop: boolean = false) {
		// Info about filtered table.
		const resp = await this._network.withAuthChecking(
			axios.post(this._infoQuery.value, this._completedQuery.value),
		);
		if (fromLoop && this.rowCountWithFilters.value !== resp.data.record_count) {
			if (this._loadedRows.value.length !== this._rowsPerPage) {
				this.isLoading.value = true;
			}

			await this.refreshRows();
			this.isLoading.value = false;
		}

		if (
			this.rowCount.value !== resp.data.all_record_count &&
			this.rowCount.value !== 0
		) {
			await this.handleNewRows(this.rowCount.value, resp.data.all_record_count);
		}

		this.pageCount.value = resp.data.page_count;
		this.rowCountWithFilters.value = resp.data.record_count;
		this.rowCount.value = resp.data.all_record_count;
	}
	/** Stores new row id's. */
	private async handleNewRows(oldCount: number, newCount: number) {
		const difference = newCount - oldCount;
		if (difference < 0) {
			return;
		}
		let rowsPerPage;
		let page;

		if (newCount - difference >= difference) {
			rowsPerPage = newCount - difference;
			page = 2;
		} else {
			rowsPerPage = newCount;
			page = 1;
		}

		const link = `${this._endpoint}${this._getEndpoint}/page/${page}?records_per_page=${rowsPerPage}`;

		const resp = await this._network.withAuthChecking(axios.post(link, {}));

		const rawRows: Array<T> = resp.data;
		const newRows = rawRows.slice(-newCount, rawRows.length);

		for (const row of newRows) {
			this._newIds.value.push(row.id);
		}
	}
	/** Updates rows. */
	private async refreshRows() {
		const resp = await this._network.withAuthChecking(
			axios.post(this._rowsQuery.value, this._completedQuery.value),
		);

		this._loadedRows.value = resp.data;

		const rowsLength = this._loadedRows.value.length;

		if (rowsLength === 0) {
			this.currentPage.value = 1;
		}

		this._highlighted.value = Array<boolean>(rowsLength).fill(
			false,
			0,
			rowsLength,
		);
		this._checked.value = Array<boolean>(rowsLength).fill(false, 0, rowsLength);

		for (let index = 0; index < this._loadedRows.value.length; index++) {
			const row = this._loadedRows.value[index];

			if (
				this._newIds.value.find((id: number) => id === row.id) !== undefined
			) {
				this._elementHighlighted(index, true);
			}
		}
	}
	/** Forces updating rows. */
	protected forceRefresh() {
		const limit = 3;
		this._refreshKey.value = (this._refreshKey.value + 1) % limit;
	}
	//#endregion

	//#region Generating query
	private _query = computed(() => {
		return `records_per_page=${this._rowsPerPage}`;
	});
	private _searchedQuery = computed((): Array<SearchSchema> => {
		return this.searchQuery.value;
	});
	private _datedQuery = computed(() => {
		return this.byDate.value;
	});
	private _filteredQuery = computed(() => {
		return [];
	});
	private _orderedQuery = computed((): OrderBySchema => {
		return {
			column: this._orderBy.value,
			desc: this.desc.value,
		};
	});
	private _completedQuery = computed((): QuerySchema => {
		return {
			search_query: this._searchedQuery.value,
			order_by_query: this._orderedQuery.value,
			date_query: this._datedQuery.value,
			filter_query: this._filteredQuery.value,
		};
	});
	private _infoQuery = computed(() => {
		return `${this._endpoint}${this._infoEndpoint}/page/info?${this._query.value}`;
	});
	private _rowsQuery = computed(() => {
		return `${this._endpoint}${this._getEndpoint}/page/${this.currentPage.value}?${this._query.value}`;
	});
	//#endregion

	private getHeaders() {
		const result: Array<string> = [];
		if (this._nonIgnoredRows.value.length === 0) return result;

		for (const fieldName in this._nonIgnoredRows.value[0]) {
			const alias = this.getAlias(fieldName);

			const index = this._columsOrder.get(fieldName);

			if (index && result.length > index) {
				result.splice(index, 0, alias);
			} else {
				result.push(alias);
			}
		}
		return result;
	}

	//#region Generating rows
	private _nonIgnoredRows = computed(() => {
		const result: Array<T> = [];

		for (let index = 0; index < this._loadedRows.value.length; index++) {
			const model: T = this._loadedRows.value[index];

			let newModel: any = {};

			for (const fieldName in model) {
				if (this._ignored.find((rule) => rule === fieldName) === undefined) {
					newModel[fieldName] = model[fieldName];
				}
			}

			result.push(newModel as T);
		}
		return result;
	});
	private _formattedOrderedRows = computed(() => {
		const result: TableData = {
			headers: this.getHeaders(),
			rows: [],
		};

		for (let index = 0; index < this._nonIgnoredRows.value.length; index++) {
			const model = this._nonIgnoredRows.value[index];
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

			result.rows.push({ id: model.id, columns: columns });
		}

		return result;
	});
	public rows = computed(() => {
		if (this.isHidden.value) {
			return { headers: this._formattedOrderedRows.value.headers, rows: [] };
		}
		return this._formattedOrderedRows.value;
	});
	//#endregion

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
	private _elementChecked(index: number, newValue: boolean) {
		this._checked.value[index] = newValue;
	}
	public checked = computed(() => {
		const result: Array<TableElementObserver<boolean>> = [];

		for (let index = 0; index < this.rows.value.rows.length; index++) {
			result.push(
				new TableElementObserver(
					this._checked.value[index],
					index,
					this._elementChecked.bind(this),
				),
			);
		}

		return result;
	});
	private _elementHighlighted(index: number, newValue: boolean) {
		this._highlighted.value[index] = newValue;

		if (!newValue) {
			const idForDelete = this._loadedRows.value[index].id;

			const deleteIndex = this._newIds.value.findIndex(
				(id: number) => id === idForDelete,
			);

			if (deleteIndex !== -1) {
				this._newIds.value.splice(deleteIndex);
			}
		}
	}
	public highlighted = computed(() => {
		const result: Array<TableElementObserver<boolean>> = [];

		for (let index = 0; index < this.rows.value.rows.length; index++) {
			result.push(
				new TableElementObserver(
					this._highlighted.value[index],
					index,
					this._elementHighlighted.bind(this),
				),
			);
		}

		return result;
	});
	public notifies = computed(() => {
		let result = 0;

		result += this._newIds.value.length;

		return result;
	});
	//#endregion

	//#region Auxiliary
	/** Table update timeout in second. */
	public updateTimeout: number = 20;
	/** Indicates current page. */
	public currentPage: Ref<number> = ref(1);
	/** Indicates page count. */
	public pageCount: Ref<number> = ref(0);
	/** Indicates row count with query filters. */
	public rowCountWithFilters: Ref<number> = ref(0);
	/** Indicates row count for all rows in table. */
	public rowCount: Ref<number> = ref(0);
	/** Rows per page. */
	protected _rowsPerPage: number = 15;
	/** True when table is execute large loading operations. */
	public isLoading: Ref<boolean> = ref(false);
	/** Hides all row if true. */
	public isHidden: Ref<boolean> = ref(false);
	/** Emulates loading by hidding table rows and setting **this.isLoading** to **true** if **value** = **true**. */
	public emulateLoading(value: boolean) {
		this.isLoading.value = value;
		this.isHidden.value = value;
	}
	/** Return **true** if rows sorted by this column with **header**. */
	public ordered(header: string): boolean {
		return this.getAlias(this._orderBy.value) === header;
	}
	/** Sorts columns by specify **header**. */
	public order(header: string) {
		if (header === this.getAlias(this._orderBy.value)) {
			this.desc.value = !this.desc.value;
			return;
		}

		if (this._loadedRows.value.length === 0) {
			return;
		}

		const column = Object.keys(this._loadedRows.value[0]).find(
			(fieldName) => this.getAlias(fieldName) === header,
		);

		if (column !== undefined) {
			this._orderBy.value = column;
			this.desc.value = false;
		}
	}
	/** If sorts column by row[**index**]. */
	protected _orderBy: Ref<string> = ref("id");
	/** If equal **true** sorted corresponding column in **DESC** mode. */
	public desc: Ref<boolean> = ref(true);
	/** Search query. */
	public searchQuery: Ref<Array<SearchSchema>> = ref([]);
	/** Date query. */
	public byDate: Ref<DateSchema | undefined> = ref();
	/** Order of column in table. */
	protected _columsOrder: Map<string, number> = new Map<string, number>();
	/** Aliases for column names. */
	protected _aliases: Map<string, string> = new Map<string, string>();
	/** Specify ingored column. */
	protected _ignored: Array<string> = [];
	/** Default forrmatter for column value. */
	protected _defaultFormatter: (value: any) => Cell = (value: any): Cell => {
		if (value === null) {
			return new Cell();
		} else {
			return new Cell(new CellLine(`${value}`));
		}
	};
	/** Formatters for column values. */
	protected _formatters: Map<string, (value: any) => Cell> = new Map<
		string,
		(value: any) => Cell
	>();
	/** Returns actual formatter for specified **fieldName**. */
	private getFormatter(fieldName: string): (value: any) => Cell {
		const formatter = this._formatters.get(fieldName);

		if (formatter) {
			return formatter;
		} else {
			return this._defaultFormatter;
		}
	}
	/** Returns actual alias for specified **fieldName**. */
	private getAlias(fieldName: string): string {
		let alias = this._aliases.get(fieldName);
		if (alias === undefined) {
			alias = fieldName;
		}
		return alias;
	}
	/** Returns count of highlighted rows. */
	public highlightedCount = computed(() => {
		let result = 0;
		for (const elemHighlighted of this._highlighted.value) {
			if (elemHighlighted) {
				result++;
			}
		}
		return result;
	});
	/** If equal **true** rows will be erase after approving or rejecting happens. */
	protected _deleteAfterStatusChanged: boolean = false;
	/** Updates **source** model by **target** model if have difference.
	 * - Returns **true** if **source** model updated, **false** otherwise.
	 */
	private updateModel(source: any, target: any): boolean {
		let modelChanged = false;

		for (const fieldName in target) {
			const formatter = this.getFormatter(fieldName);

			const targetString: string = formatter(target[fieldName]).toString();
			const sourceString: string = formatter(source[fieldName]).toString();
			source[fieldName] = target[fieldName];

			if (targetString !== sourceString) {
				modelChanged = true;
			}
		}

		return modelChanged;
	}
	/** Return model by index. */
	public getModel(index: number): any {
		return this._loadedRows.value[index];
	}
	/** Executes **action** for checked rows. */
	private async manageChecked(action: (index: number) => Promise<void>) {
		this.emulateLoading(true);
		for (let index = 0; index < this._loadedRows.value.length; index++) {
			if (this._checked.value[index]) {
				await action(index);
			}
		}
		this.forceRefresh();
		this.emulateLoading(false);
	}
	// Endpoints.
	private _endpoint: string = "";
	protected _getEndpoint: string = "";
	protected _infoEndpoint: string = "";
	protected _createEndpoint: string = "";
	protected _updateEndpoint: string = "";
	protected _deleteEndpoint: string = "";
	protected _approveEndpoint: string = "";
	protected _rejectEndpoint: string = "";
	//#endregion

	//#region CRUD
	public async create(model: T): Promise<void> {
		await this._network.withAuthChecking(
			axios.post(`${this._endpoint}${this._createEndpoint}/`, model),
		);

		await this.refreshInfo();
	}
	public async update(model: T, index: number): Promise<void> {
		let elementChanged = this.updateModel(this._loadedRows.value[index], model);

		if (elementChanged) {
			await this._network.withAuthChecking(
				axios.patch(
					`${this._endpoint}${this._updateEndpoint}/`,
					this._loadedRows.value[index],
				),
			);
		}
	}
	public async delete(
		index: number,
		needRefresh: boolean = false,
	): Promise<void> {
		await this._network.withAuthChecking(
			axios.delete(
				`${this._endpoint}${this._deleteEndpoint}/${this._loadedRows.value[index].id}`,
			),
		);

		if (needRefresh) {
			this.forceRefresh();
		}
	}
	public async deleteChecked(): Promise<void> {
		await this.manageChecked(
			async (index: number, _?: string) => await this.delete(index),
		);
	}
	public async approve(
		index: number,
		needRefresh: boolean = false,
	): Promise<void> {
		await this._network.withAuthChecking(
			axios.patch(
				`${this._endpoint}${this._approveEndpoint}/approve/${this._loadedRows.value[index].id}`,
			),
		);

		if (needRefresh) {
			this.forceRefresh();
		}
	}
	public async approveChecked(): Promise<void> {
		await this.manageChecked(
			async (index: number, _?: string) => await this.approve(index),
		);
	}
	public async reject(
		index: number,
		needRefresh: boolean = false,
		reason: string,
	): Promise<void> {
		await this._network.withAuthChecking(
			axios.patch(
				`${this._endpoint}${this._rejectEndpoint}/reject/${this._loadedRows.value[index].id}?reason=${reason}`,
			),
		);

		if (needRefresh) {
			this.forceRefresh();
		}
	}
	public async rejectChecked(reason: string): Promise<void> {
		await this.manageChecked(
			async (index: number) => await this.reject(index, false, reason),
		);
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
	constructor(options?: {
		getEndpoint?: string;
		infoEndpoint?: string;
		createEndpoint?: string;
		updateEndpoint?: string;
		deleteEndpoint?: string;
		approveEndpoint?: string;
		rejectEndpoint?: string;
	}) {
		super("bid", options);

		this._formatters.set("department", parser.formatDepartment);
		this._formatters.set("worker", parser.formatWorker);
		this._formatters.set("create_date", parser.formatDate);
		this._formatters.set("close_date", parser.formatDate);
		this._formatters.set("documents", parser.formatDocuments);
		this._formatters.set("payment_type", parser.formatPaymentType);
		this._formatters.set("expenditure", parser.formatExpenditure);

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
		this._aliases.set("denying_reason", "Причина отказа");
		this._aliases.set("documents", "Документы");
		this._aliases.set("expenditure", "Статья");

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
		this._columsOrder.set("denying_reason", 10);
		this._columsOrder.set("comment", 11);
		this._columsOrder.set("expenditure", 12);
	}
}

export class FACBidTable extends BidTable {
	constructor() {
		super({
			getEndpoint: "/fac",
			infoEndpoint: "/fac",
		});
	}
}

export class CCBidTable extends BidTable {
	constructor() {
		super({
			getEndpoint: "/cc",
			infoEndpoint: "/cc",
		});
	}
}

export class CCSupervisorBidTable extends BidTable {
	constructor() {
		super({
			getEndpoint: "/cc_supervisor",
			infoEndpoint: "/cc_supervisor",
		});
	}
}
//#endregion
