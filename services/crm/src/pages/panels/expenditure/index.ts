import { Table } from "@/components/table";
import { ExpenditureSchema, RouteData } from "@/types";
import * as parser from "@/parser";
import { SearchModelOut, useSearch } from "@/hooks/tableSearchHook";

interface ExpenditurePanelData {
	searchList: SearchModelOut[];
}

export class ExpenditureTable extends Table<ExpenditureSchema> {
	constructor() {
		super("expenditure");
		this._formatters.set("fac", parser.formatWorker);
		this._formatters.set("cc", parser.formatWorker);
		this._formatters.set("paralegal", parser.formatWorker);
		this._formatters.set("creator", parser.formatWorker);
		this._formatters.set("create_date", parser.formatDateTime);

		this._aliases.set("id", "ID");
		this._aliases.set("name", "Статья");
		this._aliases.set("chapter", "Раздел");
		this._aliases.set("create_date", "Дата создания");
		this._aliases.set("fac", "ЦФО");
		this._aliases.set("cc", "ЦЗ");
		this._aliases.set("paralegal", "Юрисконсульт");
		this._aliases.set("creator", "Создал");
	}
}

export async function setupExpenditre(
	table: ExpenditureTable,
	routeData: RouteData,
): Promise<ExpenditurePanelData> {
	const searchList = await useSearch(table, routeData, {
		schemas: [
			{
				pattern: "fac",
				groups: [0],
			},
			{
				pattern: "chapter",
				groups: [1],
			},
			{
				pattern: "name",
				groups: [2],
			},
		],
		placeholder: "Поиск",
		style: "height: 100%; width: 170px",
		name: "general",
	});

	return { searchList };
}
