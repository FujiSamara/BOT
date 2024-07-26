import { Access, PanelData } from "@/types";
import BidPanel from "@/panels/BidPanel.vue";
import ExpenditurePanel from "@/panels/ExpenditurePanel.vue";
import BudgetPanel from "@/panels/BudgetPanel.vue";
import { shallowRef } from "vue";

const panels: Array<PanelData> = [
	{
		id: 1,
		imageSrc: "/img/expenditure_logo.svg",
		label: "Статьи",
		isActive: false,
		panel: shallowRef(ExpenditurePanel),
		access: Access.Expenditure,
	},
	{
		id: 2,
		imageSrc: "/img/budget_logo.svg",
		label: "Бюджет",
		isActive: false,
		panel: shallowRef(BudgetPanel),
		access: Access.Budget,
	},
	{
		id: 3,
		imageSrc: "/img/bid_logo.svg",
		label: "Заявки",
		isActive: false,
		panel: shallowRef(BidPanel),
		access: Access.Bid,
	},
];

export function getPanelsByAccesses(accesses: Array<Access>): Array<PanelData> {
	const result: Array<PanelData> = [];

	for (let j = 0; j < panels.length; j++) {
		const panel = panels[j];

		for (let i = 0; i < accesses.length; i++) {
			const access = accesses[i];

			if (panel.access === access || access === Access.Admin) {
				result.push(panel);
				break;
			}
		}
	}

	return result;
}
