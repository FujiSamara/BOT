import { Table } from "@/components/table";
import { BaseSchema } from "@/types";
import { nextTick, ShallowRef } from "vue";

type TableMap = Map<string, Table<BaseSchema>>;

export class TableService {
	private _tables: TableMap;

	constructor(
		private tableContainer: Readonly<ShallowRef<HTMLDivElement | null>>,
	) {
		this._tables = new Map() as TableMap;
	}

	private async measureTableHeight(): Promise<number | undefined> {
		if (!this.tableContainer.value) {
			return;
		}

		let tableElement: HTMLElement;

		do {
			tableElement = this.tableContainer.value.getElementsByClassName(
				"table",
			)[0] as HTMLElement;
			await nextTick();
		} while (!tableElement);

		return tableElement.offsetHeight;
	}

	private async setRowsCount() {
		const tableHeight = await this.measureTableHeight();

		if (!tableHeight) {
			return;
		}

		const rowCount = Math.floor((tableHeight - 72) / 64);

		for (const el of this._tables) {
			el[1].rowsPerPage.value = rowCount;
		}
	}

	public register(name: string, CustomTable: { new (): Table<BaseSchema> }) {
		const table = new CustomTable();
		this._tables.set(name, table);
	}

	public async startLoops() {
		await this.setRowsCount();

		for (const el of this._tables) {
			el[1].startUpdatingLoop();
		}
	}

	public get(name: string): Table<BaseSchema> | undefined {
		const table = this._tables.get(name);

		if (!table) return undefined;

		return table;
	}
}
