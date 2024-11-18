import { Access, PanelData } from "@/types";
import BidPanel from "@/panels/BidPanel.vue";
import BidPanelReadOnly from "@/panels/BidPanelReadOnly.vue";
import FACAndCCBidPanel from "@/panels/FACAndCCBidPanel.vue";
import FACAndCCBidHistoryPanel from "@/panels/FACAndCCBidHistoryPanel.vue";
import CCSupervisorBidPanel from "@/panels/CCSupervisorBidPanel.vue";
import AccountantCardBidPanel from "@/panels/AccountantCardBidPanel.vue";
import ExpenditurePanel from "@/panels/ExpenditurePanel.vue";
import BudgetPanel from "@/panels/BudgetPanel.vue";
import WorkTimePanel from "@/panels/WorkTimePanel.vue";
import { shallowRef } from "vue";
import MyBidPanel from "@/panels/MyBidPanel.vue";
import ArchiveBidPanel from "@/panels/ArchiveBidPanel.vue";

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
	{
		id: 4,
		imageSrc: "/img/bid_logo.svg",
		label: "Заявки пр.",
		isActive: false,
		panel: shallowRef(BidPanelReadOnly),
		access: Access.BidReadOnly,
	},
	{
		id: 5,
		imageSrc: "/img/bid_logo.svg",
		label: "Заявки на соглас.",
		isActive: false,
		panel: shallowRef(FACAndCCBidPanel),
		access: Access.FAC_CCbid,
	},
	{
		id: 6,
		imageSrc: "/img/bid_logo.svg",
		label: "История соглас.",
		isActive: false,
		panel: shallowRef(FACAndCCBidHistoryPanel),
		access: Access.FAC_CCbid,
	},
	{
		id: 7,
		imageSrc: "/img/bid_logo.svg",
		label: "Заявки ЮК",
		isActive: false,
		panel: shallowRef(CCSupervisorBidPanel),
		access: Access.CCSupervisorBid,
	},
	{
		id: 8,
		imageSrc: "/img/bid_logo.svg",
		label: "Заявки бух.",
		isActive: false,
		panel: shallowRef(AccountantCardBidPanel),
		access: Access.AccountantCardBid,
	},
	{
		id: 9,
		imageSrc: "/img/worktime.svg",
		label: "Явки",
		isActive: false,
		panel: shallowRef(WorkTimePanel),
		access: Access.Worktime,
	},
	{
		id: 10,
		imageSrc: "/img/bid_logo.svg",
		label: "Мои заявки",
		isActive: false,
		panel: shallowRef(MyBidPanel),
		access: Access.MyBid,
	},
	{
		id: 11,
		imageSrc: "/img/bid_logo.svg",
		label: "Архив заявок",
		isActive: false,
		panel: shallowRef(ArchiveBidPanel),
		access: Access.ArchiveBid,
	},
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
