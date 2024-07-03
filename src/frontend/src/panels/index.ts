import { Access, PanelData } from "@/types";
import BidPanel from "@/panels/BidPanel.vue";
import BudgetPanel from "@/panels/BudgetPanel.vue";
import { shallowRef } from "vue";

const panels: Array<PanelData> = [
	{
		id: 1,
		imageSrc: "/img/bid_logo.svg",
		label: "Заявки",
		isActive: false,
		panel: shallowRef(BidPanel),
		access: Access.Bid,
	},
	{
		id: 2,
		imageSrc: "/img/bid_logo.svg",
		label: "Бюджет",
		isActive: false,
		panel: shallowRef(BudgetPanel),
		access: Access.Budget,
	},
];

export function getPanelsByAccesses(accesses: Array<Access>): Array<PanelData> {
	const result: Array<PanelData> = [];

	for (let i = 0; i < accesses.length; i++) {
		const access = accesses[i];

		for (let j = 0; j < panels.length; j++) {
			const panel = panels[j];

			if (panel.access === access) result.push(panel);
		}
	}

	return result;
}
