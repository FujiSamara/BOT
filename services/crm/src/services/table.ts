import { Table } from "@/components/table";
import { BaseSchema } from "@/types";
import { ShallowRef } from "vue";

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

		const table = await new Promise<HTMLElement>((resolve) => {
			if (!this.tableContainer.value) {
				return;
			}

			const observer = new MutationObserver((_) => {
				if (!this.tableContainer.value) {
					return;
				}
				const element = this.tableContainer.value.querySelector(".table");

				if (element) {
					observer.disconnect();
					resolve(element as HTMLElement);
				}
			});

			observer.observe(this.tableContainer.value, {
				childList: true,
				subtree: true,
			});
		});

		return table.offsetHeight;
	}

	private async setRowsCount() {
		const tableHeight = await this.measureTableHeight();
		if (!tableHeight) {
			return;
		}

		const rowHeight = parseInt(
			window
				.getComputedStyle(document.documentElement)
				.getPropertyValue("--row-height"),
		);

		const rowCount = Math.floor((tableHeight - 72) / rowHeight);
		for (const el of this._tables) {
			el[1].rowsPerPage.value = rowCount;
		}
	}

	public register(
		name: string,
		CustomTable: { new (): Table<BaseSchema> },
		withLoop: boolean = true,
	) {
		const table = new CustomTable();
		table.blockLoop.value = !withLoop;
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
