import { Table } from "@/components/table";
import { BaseSchema } from "@/types";

type TableMap = Map<string, Table<BaseSchema>>;

export class TableService {
	private _tables: TableMap;

	constructor() {
		this._tables = new Map() as TableMap;
	}

	public register(name: string, CustomTable: { new (): Table<BaseSchema> }) {
		const table = new CustomTable();
		this._tables.set(name, table);
		table.startUpdatingLoop();
	}

	public get(name: string): Table<BaseSchema> | undefined {
		const table = this._tables.get(name);

		if (!table) return undefined;

		return table;
	}
}
