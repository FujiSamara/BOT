import { ShallowRef } from "vue";

export interface NavigationData {
	id: number;
	imageSrc: string;
	label: string;
	isActive: boolean;
	notifyCount?: number;
}

export enum Access {
	Bid,
	Expenditure,
}

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
	limit: number;
	create_date: Date;
	fac: WorkerSchema;
	cc: WorkerSchema;
	cc_supervisor: WorkerSchema;
}
