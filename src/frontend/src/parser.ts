import { DepartmentSchema, ExpenditureSchema, WorkerSchema } from "@/types";

export function formatWorker(worker: WorkerSchema): string {
	return `${worker.l_name} ${worker.f_name} ${worker.o_name}`;
}

export function formatDate(dateString: string): string {
	const date = new Date(dateString);
	return date.toLocaleString();
}

export function formatExpenditure(expenditure: ExpenditureSchema): string {
	return `${expenditure.name}/${expenditure.chapter}`;
}

export function formatDepartment(department: DepartmentSchema): string {
	if (!department) return "Не указано";
	return department.name;
}
