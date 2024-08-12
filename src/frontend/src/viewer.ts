import { Cell, CellLine } from "@/table";
import { BaseSchema, BidSchema } from "@/types";
import * as parser from "@/parser";

class HeaderedCell extends Cell {
	constructor(
		public header: string,
		...cellLines: Array<CellLine>
	) {
		super(...cellLines);
	}
}

export class Viewer<T extends BaseSchema> {
	// #region Viewer settings
	/** Formatters for istances values */
	protected _formatters: Map<string, (value: any) => Cell> = new Map<
		string,
		(value: any) => Cell
	>();
	/** Aliases for column names */
	protected _aliases: Map<string, string> = new Map<string, string>();
	protected _defaultFormatter: (value: any) => Cell = (value: any): Cell => {
		if (value === null) {
			return new Cell();
		} else {
			return new Cell(new CellLine(`${value}`));
		}
	};
	private getFormatter(fieldName: string): (value: any) => Cell {
		const formatter = this._formatters.get(fieldName);

		if (formatter) {
			return formatter;
		} else {
			return this._defaultFormatter;
		}
	}
	private getAlias(fieldName: string): string {
		let alias = this._aliases.get(fieldName);
		if (alias === undefined) {
			alias = fieldName;
		}
		return alias;
	}
	// #endregion

	public fields: Array<HeaderedCell> = [];

	protected initFields(model: T) {
		for (const fieldName in model) {
			const alias = this.getAlias(fieldName);
			const formatter = this.getFormatter(fieldName);
			const value = formatter(model[fieldName]);

			this.fields.push(new HeaderedCell(alias, ...value.cellLines));
		}
	}
}

//#region Viewers
export class BidViewer extends Viewer<BidSchema> {
	constructor(model: BidSchema) {
		super();

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
		this._aliases.set("denying_reason", "Причина отказа");
		this._aliases.set("documents", "Документы");

		this.initFields(model);
	}
}
//#endregion
