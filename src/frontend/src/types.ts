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
}

export const accessesDict: any = {
	admin: Access.Admin,
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

export interface BidSchema extends BaseSchema {
	amount: number;
	payment_type: string;
	department: DepartmentSchema;
	worker: WorkerSchema;
	purpose: string;
	create_date: Date;
	close_date: Date;
	documents: string;
	status: string;
	comment: string;
}
