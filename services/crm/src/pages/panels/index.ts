import { Access, PanelData, TableData } from "@types";
import { ExpenditureTable } from "@/pages/panels/expenditure";
import { WorktimeTable } from "@/pages/panels/worktime";
import { TimesheetTable } from "@/pages/panels/timesheet";
import {
	AccountantCardBidTable,
	BidTable,
	FACAndCCBidHistoryTable,
	FACAndCCBidTable,
	MyBidTable,
	ParalegalBidTable,
	ArchiveBidTable,
} from "@/pages/panels/bid";

const tables: Array<TableData> = [
	{
		label: "Статьи",
		routeName: "table-expenditures",
		iconURL: "/img/expenditure.svg",
		active: false,
		name: "expenditure",
		create: ExpenditureTable,
		accesses: [Access.Expenditure],
	},
	{
		label: "Явки",
		routeName: "table-worktimes",
		iconURL: "/img/watch.svg",
		active: false,
		name: "worktime",
		create: WorktimeTable,
		accesses: [Access.Worktime],
	},
	{
		label: "Табель",
		routeName: "table-timesheets",
		iconURL: "/img/timesheet.svg",
		active: false,
		name: "timesheet",
		create: TimesheetTable,
		accesses: [Access.Worktime],
		withUpdatingLoop: false,
	},
	{
		label: "Заявки (админ)",
		routeName: "table-bids",
		iconURL: "/img/coins.svg",
		active: false,
		name: "bid",
		create: BidTable,
		accesses: [Access.Bid],
	},
	{
		label: "Заявки",
		routeName: "table-readonly-bids",
		iconURL: "/img/coins.svg",
		active: false,
		name: "readonlybid",
		create: BidTable,
		accesses: [Access.BidReadOnly],
	},
	{
		label: "Заявки на согласование",
		routeName: "table-fac-cc-bids",
		iconURL: "/img/coins.svg",
		active: false,
		name: "facccbid",
		create: FACAndCCBidTable,
		accesses: [Access.FAC_CCbid],
	},
	{
		label: "История согласование",
		routeName: "table-fac-cc-history-bids",
		iconURL: "/img/coins.svg",
		active: false,
		name: "faccchistorybid",
		create: FACAndCCBidHistoryTable,
		accesses: [Access.FAC_CCbid],
	},
	{
		label: "Заявки Юристконсульт",
		routeName: "table-paralegal-bids",
		iconURL: "/img/coins.svg",
		active: false,
		name: "paralegalbid",
		create: ParalegalBidTable,
		accesses: [Access.ParalegalBid],
	},
	{
		label: "Заявки бухгалтера",
		routeName: "table-accountant-card-bids",
		iconURL: "/img/coins.svg",
		active: false,
		name: "accountantcardbid",
		create: AccountantCardBidTable,
		accesses: [Access.AccountantCardBid],
	},
	{
		label: "Мои заявки",
		routeName: "table-my-bids",
		iconURL: "/img/coins.svg",
		active: false,
		name: "mybid",
		create: MyBidTable,
		accesses: [Access.MyBid],
	},
	{
		label: "Архив заявок",
		routeName: "table-archive-bids",
		iconURL: "/img/coins.svg",
		active: false,
		name: "archivebid",
		create: ArchiveBidTable,
		accesses: [Access.ArchiveBid],
	},
];
const knowledge: Array<PanelData> = [
	{
		label: "Продукт",
		routeName: "knowledge-product",
		iconURL: "/img/product.svg",
		active: false,
		name: "product",
		accesses: [Access.ProductRead],
		writeAccesses: [Access.ProductWrite],
	},
	{
		label: "Маркетинг",
		routeName: "knowledge-marketing",
		iconURL: "/img/bag.svg",
		active: false,
		name: "marketing",
		accesses: [Access.MarketingRead],
		writeAccesses: [Access.MarketingWrite],
	},
	{
		label: "Персонал",
		routeName: "knowledge-staff",
		iconURL: "/img/staff.svg",
		active: false,
		name: "staff",
		accesses: [Access.StaffRead],
		writeAccesses: [Access.StaffWrite],
	},
	{
		label: "Закупки",
		routeName: "knowledge-purchases",
		iconURL: "/img/bag.svg",
		active: false,
		name: "purchases",
		accesses: [Access.PurchasesRead],
		writeAccesses: [Access.PurchasesWrite],
	},
	{
		label: "ЦД",
		routeName: "knowledge-cd",
		iconURL: "/img/car.svg",
		active: false,
		name: "cd",
		accesses: [Access.CdRead],
		writeAccesses: [Access.CdWrite],
	},
	{
		label: "Контроль",
		routeName: "knowledge-control",
		iconURL: "/img/shield.svg",
		active: false,
		name: "control",
		accesses: [Access.ControlRead],
		writeAccesses: [Access.ControlWrite],
	},
	{
		label: "Учет",
		routeName: "knowledge-accounting",
		iconURL: "/img/safe.svg",
		active: false,
		name: "accounting",
		accesses: [Access.AccountingRead],
		writeAccesses: [Access.AccountingWrite],
	},

	{
		label: "Поиск",
		routeName: "knowledge-search",
		iconURL: "/img/product.svg",
		active: false,
		name: "stub",
		accesses: [Access.Authed],
	},
];

const panels: Array<PanelData> = [...tables, ...knowledge];

function getByAccesses<T extends PanelData>(
	accesses: Array<Access>,
	panels: Array<T>,
): Array<T> {
	const result: Array<T> = [];

	for (let j = 0; j < panels.length; j++) {
		const panel = panels[j];

		const accessesExist = panel.accesses.map((_) => false);

		for (let i = 0; i < accesses.length; i++) {
			const access = accesses[i];

			for (let index = 0; index < accessesExist.length; index++) {
				const neededAccess = panel.accesses[index];

				if (neededAccess === access || access === Access.Admin) {
					accessesExist[index] = true;
				}
			}
		}
		if (accessesExist.every((accessExist) => accessExist)) {
			result.push(panel);
		}
	}

	return result;
}

export function getPanelsByAccesses(accesses: Array<Access>): Array<PanelData> {
	return getByAccesses(accesses, panels);
}

export function getTablesByAccesses(accesses: Array<Access>): Array<TableData> {
	return getByAccesses(accesses, tables);
}

export function getKnowledgeByAccesses(
	accesses: Array<Access>,
): Array<PanelData> {
	return getByAccesses(accesses, knowledge);
}

export function canEditPanel(
	accesses: Array<Access>,
	panel: PanelData,
): boolean {
	if (panel.writeAccesses === undefined) return true;

	return panel.writeAccesses.every((neededAccess) =>
		accesses.some(
			(access) => neededAccess === access || access === Access.Admin,
		),
	);
}
