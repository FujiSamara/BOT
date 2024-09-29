import { ShallowRef } from "vue";

export interface NavigationData {
	id: number;
	imageSrc: string;
	label: string;
	isActive: boolean;
	notifyCount?: number;
}

export interface Token {
	access_token: string;
	token_type: string;
}

export enum Access {
	Bid,
	Expenditure,
	Budget,
	Admin,
	FACBid,
	CCBid,
	CCSupervisorBid,
	Worktime,
	Authed,
}

export const accessesDict: any = {
	admin: Access.Admin,
	crm_bid: Access.Bid,
	crm_budget: Access.Budget,
	crm_expenditure: Access.Expenditure,
	crm_fac_bid: Access.FACBid,
	crm_cc_bid: Access.CCBid,
	crm_cc_supervisor_bid: Access.CCSupervisorBid,
	authenticated: Access.Authed,
};

export interface PanelData extends NavigationData {
	panel: ShallowRef<any>;
	access: Access;
}

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
	cc_supervisor: WorkerSchema;
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
