import { ExpenditureSchema, Table } from "@/types";
import axios from "axios";
import * as config from "@/config";

class PanelDataHandler<T> {
	private _schemas: Array<T> = [];

	constructor(
		private _table: Table,
		private _endpoint: string,
		private _toSchema: (model: any) => T,
		private _toRow: (schema: T) => Array<string>,
	) {}

	public async loadData() {
		const resp = await axios.get(`${this._endpoint}s`);

		if (resp.status < 400) {
			const models = resp.data.dumps;

			for (let index = 0; index < models.length; index++) {
				const model = models[index];
				const schema = this._toSchema(model);
				this._schemas.push(schema);
				this._table.push(this._toRow(schema));
			}
		}
	}
	public async deleteRow(rowKey: number) {}
	public async updateRow(rowKey: number, row: Object) {}
	public async addRow(row: Array<string>) {}
}

export default function usePanelDataHandler(
	table: Table,
	panelName: string,
): PanelDataHandler<any> | undefined {
	const endpoint = `http://${config.backendDomain}:${config.backendPort}/${config.crmEndpoint}/panel/${panelName}`;

	switch (panelName) {
		case "expenditure":
			return new PanelDataHandler<ExpenditureSchema>(
				table,
				endpoint,
				toExpenditureSchema,
				expenditureToRow,
			);
		default:
			break;
	}
}

function toExpenditureSchema(expenditure: any): ExpenditureSchema {
	return {
		id: expenditure.id,
		name: expenditure.name,
		chapter: expenditure.chapter,
		create_date: expenditure.create_date,
		limit: expenditure.limit,
		fac: {
			id: expenditure.fac.id,
			f_name: expenditure.fac.f_name,
			l_name: expenditure.fac.l_name,
			o_name: expenditure.fac.o_name,
		},
		cc: {
			id: expenditure.cc.id,
			f_name: expenditure.cc.f_name,
			l_name: expenditure.cc.l_name,
			o_name: expenditure.cc.o_name,
		},
		cc_supervisor: {
			id: expenditure.cc_supervisor.id,
			f_name: expenditure.cc_supervisor.f_name,
			l_name: expenditure.cc_supervisor.l_name,
			o_name: expenditure.cc_supervisor.o_name,
		},
	};
}

function expenditureToRow(expenditure: ExpenditureSchema): Array<string> {
	return [
		`${expenditure.id}`,
		`${expenditure.name}`,
		`${expenditure.chapter}`,
		`${expenditure.create_date}`,
		`${expenditure.fac.l_name} ${expenditure.fac.f_name}`,
		`${expenditure.cc.l_name} ${expenditure.cc.f_name}`,
		`${expenditure.cc_supervisor.l_name} ${expenditure.cc_supervisor.f_name}`,
		`${expenditure.limit}`,
	];
}
