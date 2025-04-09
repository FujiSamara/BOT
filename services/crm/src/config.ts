import { Access } from "@types";

export const crmEndpoint = "api/crm";
export const authEndpoint = "api/auth";
export const filesEndpoint = "api/download";
export const knowledgeEndpoint = "api";

export const coreURL = import.meta.env.VITE_CORE_URL;
export const knowledgeURL = import.meta.env.VITE_KNOWLEDGE_URL;

export const FullKnowledgeEndpoint = `${knowledgeURL}/${knowledgeEndpoint}`;

export const cookiesExpires = "7d";

export const accessesDict: any = {
	admin: Access.Admin,
	crm_bid: Access.Bid,
	crm_budget: Access.Budget,
	crm_expenditure: Access.Expenditure,
	crm_fac_cc_bid: Access.FAC_CCbid,
	crm_paralegal_bid: Access.ParalegalBid,
	authenticated: Access.Authed,
	crm_my_bid: Access.MyBid,
	crm_archive_bid: Access.ArchiveBid,
	crm_my_file: Access.MyFile,
	crm_bid_readonly: Access.BidReadOnly,
	crm_worktime: Access.Worktime,
	crm_accountant_card_bid: Access.AccountantCardBid,
};

export const colors = {
	holiday: "#519BCA",
};
