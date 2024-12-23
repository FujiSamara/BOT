import { Table } from "@/components/table";
import { LocationQueryRaw } from "vue-router";

export interface LinkData {
	label: string;
	iconURL: string;
	routeName: string;
	active: boolean;
	name?: string;
	query?: LocationQueryRaw;
}

export interface PanelData extends LinkData {
	accesses: Access[];
	name: string;
	create: { new (): Table<BaseSchema> };
	withUpdatingLoop?: boolean;
}

export interface Token {
	access_token: string;
	token_type: string;
}

export enum Access {
	Bid,
	BidReadOnly,
	Expenditure,
	Budget,
	Admin,
	FAC_CCbid,
	CCSupervisorBid,
	Worktime,
	Authed,
	MyBid,
	ArchiveBid,
	MyFile,
	AccountantCardBid,
}

export const accessesDict: any = {
	admin: Access.Admin,
	crm_bid: Access.Bid,
	crm_budget: Access.Budget,
	crm_expenditure: Access.Expenditure,
	crm_fac_cc_bid: Access.FAC_CCbid,
	crm_paralegal_bid: Access.CCSupervisorBid,
	authenticated: Access.Authed,
	crm_my_bid: Access.MyBid,
	crm_archive_bid: Access.ArchiveBid,
	crm_my_file: Access.MyFile,
	crm_bid_readonly: Access.BidReadOnly,
	crm_worktime: Access.Worktime,
	crm_accountant_card_bid: Access.AccountantCardBid,
};

export enum DateType {
	Interval = "Интервал",
	Month = "Месяц",
	Day = "День",
}

export enum CalendarType {
	Day,
	Month,
	Year,
}

// #region Schemas

export interface BaseSchema {
	id: number;
}

export interface WorkerSchema extends BaseSchema {
	f_name: string;
	l_name: string;
	o_name: string;
}

export interface ExpenditureSchema extends BaseSchema {
	name: string;
	chapter: string;
	create_date: Date;
	fac: WorkerSchema;
	cc: WorkerSchema;
	paralegal: WorkerSchema;
}

export interface BudgetSchema extends BaseSchema {
	limit: number;
	expenditure: ExpenditureSchema;
}

export interface DepartmentSchema extends BaseSchema {
	name: string;
}

export interface DocumentSchema {
	name: string;
	href: string;
	forceHref?: boolean;
	file?: Blob;
}

export interface BidSchema extends BaseSchema {
	amount: number;
	payment_type: string;
	department: DepartmentSchema;
	worker: WorkerSchema;
	purpose: string;
	create_date: Date;
	close_date: Date;
	documents: Array<DocumentSchema>;
	status: string;
	comment: string;
	need_edm: boolean;
	activity_type: string;
}

export interface PostSchema extends BaseSchema {
	name: string;
}

export interface WorkTimeSchema extends BaseSchema {
	worker?: WorkerSchema;
	department?: DepartmentSchema;
	post?: PostSchema;

	work_begin?: string;
	work_end?: string;
	day: string;
	work_duration: Number;

	rating?: Number;
	fine?: Number;
}

export interface OrderBySchema {
	column: string;
	desc: boolean;
}

export interface SearchSchema {
	column: string;
	term: string;
	dependencies?: Array<SearchSchema>;
	groups?: Array<number>;
}

export interface DateSchema {
	column: string;
	start: Date;
	end: Date;
}

export interface FilterSchema {
	column: string;
	value: any;
	dependencies?: Array<FilterSchema>;
	groups?: Array<number>;
}

export interface QuerySchema {
	search_query?: Array<SearchSchema>;
	order_by_query?: OrderBySchema;
	date_query?: DateSchema;
	filter_query?: Array<FilterSchema>;
}

export interface TimesheetSchema extends BaseSchema {
	worker_fullname: string;
	post_name: string;
	total_hours: number;
}
// #endregion
