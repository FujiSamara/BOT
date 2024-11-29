import { Access, PanelData } from "@types";

const panels: Array<PanelData> = [
	{
		label: "Статьи",
		routeName: "table-expenditures",
		iconURL: "/src/assets/icons/expenditure.svg",
		active: false,
		accesses: [Access.Expenditure],
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
