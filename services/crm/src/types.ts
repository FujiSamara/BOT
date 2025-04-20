import { Table } from "@/components/table";
import {
	LocationQueryRaw,
	RouteLocationNormalizedLoaded,
	Router,
} from "vue-router";

export interface LinkData {
	label: string;
	iconURL: string;
	routeName: string;
	active: boolean;
	name?: string;
	query?: LocationQueryRaw;
}

export interface PanelData extends LinkData {
	name: string;
	accesses: Access[];
	writeAccesses?: Access[];
}

export interface TableData extends PanelData {
	create: { new (): Table<BaseSchema> };
	withUpdatingLoop?: boolean;
}

export interface RouteData {
	router: Router;
	route: RouteLocationNormalizedLoaded<any>;
}

export interface Token {
	access_token: string;
	token_type: string;
}

export interface InfoSchema {
	record_count: number;
	all_record_count: number;
	page_count: number;
}

export enum Access {
	Bid,
	BidReadOnly,
	Expenditure,
	Budget,
	Admin,
	FAC_CCbid,
	ParalegalBid,
	Worktime,
	Authed,
	MyBid,
	ArchiveBid,
	MyFile,
	AccountantCardBid,

	// KnowledgeBase
	ProductRead,
	MarketingRead,
	StaffRead,
	PurchasesRead,
	CdRead,
	ControlRead,
	AccountingRead,

	ProductWrite,
	MarketingWrite,
	StaffWrite,
	PurchasesWrite,
	CdWrite,
	ControlWrite,
	AccountingWrite,
}

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

	crm_product_read: Access.ProductRead,
	crm_marketing_read: Access.MarketingRead,
	crm_staff_read: Access.StaffRead,
	crm_purchases_read: Access.PurchasesRead,
	crm_cd_read: Access.CdRead,
	crm_control_read: Access.ControlRead,
	crm_accounting_read: Access.AccountingRead,

	crm_product_write: Access.ProductWrite,
	crm_marketing_write: Access.MarketingWrite,
	crm_staff_write: Access.StaffWrite,
	crm_purchases_write: Access.PurchasesWrite,
	crm_cd_write: Access.CdWrite,
	crm_control_write: Access.ControlWrite,
	crm_accounting_write: Access.AccountingWrite,
};

export enum DateType {
	Interval = "Интервал",
	Month = "Месяц",
	Day = "День",
}

export enum CalendarType {
	Day,
	Month,
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
	raw?: boolean; // If true then request sends without auth.
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
	id?: number;
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

export interface ShiftDurationSchema extends BaseSchema {
	worktime_id: number;
	duration: number;
}
export interface TimesheetSchema extends BaseSchema {
	worker_fullname: string;
	post_name: string;
	total_hours: number;
}
// #endregion

// #region Query
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
// #endregion
