import { Cell, CellLine } from "@/table";
import { BaseSchema, BidSchema } from "@/types";

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

	constructor(model: T) {
		this.initFields(model);
	}

	public fields: Array<HeaderedCell> = [];

	private initFields(model: T) {
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
		super(model);
	}
}
//#endregion
