import { Access, PanelData } from "@types";
import { ExpenditureTable } from "@/pages/panels/expenditure";
import { WorktimeTable } from "@/pages/panels/worktime";
import { TimesheetTable } from "@/pages/panels/timesheet";
import { BidTable } from "@/pages/panels/bid";

const panels: Array<PanelData> = [
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
		label: "Заявки",
		routeName: "table-bids",
		iconURL: "/img/coins.svg",
		active: false,
		name: "bid",
		create: BidTable,
		accesses: [Access.Bid],
	},
];

export function getPanelsByAccesses(accesses: Array<Access>): Array<PanelData> {
	const result: Array<PanelData> = [];

	for (let j = 0; j < panels.length; j++) {
		const panel = panels[j];

		const accessesExist = panel.accesses.map((_) => false);
		let accessGranted = true;

		for (let i = 0; i < accesses.length; i++) {
			const access = accesses[i];

			for (let index = 0; index < accessesExist.length; index++) {
				const neededAccess = panel.accesses[index];

				if (neededAccess === access || access === Access.Admin) {
					accessesExist[index] = true;
				}
			}
		}
		for (const accessExist of accessesExist) {
			if (!accessExist) {
				accessGranted = false;
				break;
			}
		}

		if (accessGranted) {
			result.push(panel);
		}
	}

	return result;
}
