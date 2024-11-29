import { defineStore } from "pinia";
import { Table } from "@/components/table";
import { BaseSchema } from "@/types";

export const useTablesStore = defineStore("tables", {
	state: () => ({
		_tables: new Map(),
	}),
	actions: {
		register(name: string, CustomTable: { new (): Table<BaseSchema> }) {
			const table = new CustomTable();
			this._tables.set(name, table);
			table.startUpdatingLoop();
		},
		get(name: string): Table<BaseSchema> | undefined {
			return this._tables.get(name);
		},
		async waitLoad(name: string) {
			const table = this.get(name);

			if (table === undefined) {
				return;
			}
		},
	},
});
