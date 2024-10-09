import { Access, PanelData } from "@/types";
import BidPanel from "@/panels/BidPanel.vue";
import FACBidPanel from "@/panels/FACBidPanel.vue";
import CCBidPanel from "@/panels/CCBidPanel.vue";
import CCSupervisorBidPanel from "@/panels/CCSupervisorBidPanel.vue";
import ExpenditurePanel from "@/panels/ExpenditurePanel.vue";
import BudgetPanel from "@/panels/BudgetPanel.vue";
import WorkTimePanel from "@/panels/WorkTimePanel.vue";
import { shallowRef } from "vue";
import MyBidPanel from "@/panels/MyBidPanel.vue";
import ArchiveBidPanel from "@/panels/ArchiveBidPanel.vue";

const panels: Array<PanelData> = [
	// {
	// 	id: 1,
	// 	imageSrc: "/img/expenditure_logo.svg",
	// 	label: "Статьи",
	// 	isActive: false,
	// 	panel: shallowRef(ExpenditurePanel),
	// 	access: Access.Expenditure,
	// },
	// {
	// 	id: 2,
	// 	imageSrc: "/img/budget_logo.svg",
	// 	label: "Бюджет",
	// 	isActive: false,
	// 	panel: shallowRef(BudgetPanel),
	// 	access: Access.Budget,
	// },
	// {
	// 	id: 3,
	// 	imageSrc: "/img/bid_logo.svg",
	// 	label: "Заявки",
	// 	isActive: false,
	// 	panel: shallowRef(BidPanel),
	// 	access: Access.Bid,
	// },
	// {
	// 	id: 4,
	// 	imageSrc: "/img/bid_logo.svg",
	// 	label: "Заявки ЦФО",
	// 	isActive: false,
	// 	panel: shallowRef(FACBidPanel),
	// 	access: Access.FACBid,
	// },
	// {
	// 	id: 5,
	// 	imageSrc: "/img/bid_logo.svg",
	// 	label: "Заявки ЦЗ",
	// 	isActive: false,
	// 	panel: shallowRef(CCBidPanel),
	// 	access: Access.CCBid,
	// },
	// {
	// 	id: 6,
	// 	imageSrc: "/img/bid_logo.svg",
	// 	label: "Заявки РЦЗ",
	// 	isActive: false,
	// 	panel: shallowRef(CCSupervisorBidPanel),
	// 	access: Access.CCSupervisorBid,
	// },
	{
		id: 7,
		imageSrc: "/img/worktime.svg",
		label: "Явки",
		isActive: false,
		panel: shallowRef(WorkTimePanel),
		access: Access.Worktime,
	},
	// {
	// 	id: 8,
	// 	imageSrc: "/img/bid_logo.svg",
	// 	label: "Мои заявки",
	// 	isActive: false,
	// 	panel: shallowRef(MyBidPanel),
	// 	access: Access.MyBid,
	// },
	// {
	// 	id: 9,
	// 	imageSrc: "/img/bid_logo.svg",
	// 	label: "Архив заявок",
	// 	isActive: false,
	// 	panel: shallowRef(ArchiveBidPanel),
	// 	access: Access.ArchiveBid,
	// },
];

export function getPanelsByAccesses(accesses: Array<Access>): Array<PanelData> {
	const result: Array<PanelData> = [];

	for (let j = 0; j < panels.length; j++) {
		const panel = panels[j];

		for (let i = 0; i < accesses.length; i++) {
			const access = accesses[i];

			if (panel.access === access || access === Access.Admin) {
				panel.isActive = false;
				result.push(panel);
				break;
			}
		}
	}

	return result;
}
