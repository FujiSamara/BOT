import {
	DepartmentSchema,
	DocumentSchema,
	ExpenditureSchema,
	WorkerSchema,
} from "@/types";

export function formatWorker(worker: WorkerSchema): string {
	if (!worker) return "Не указано";
	return `${worker.l_name} ${worker.f_name} ${worker.o_name}`;
}

export function formatDate(dateString: string): string {
	const date = new Date(dateString);
	return date.toLocaleString();
}

export function formatExpenditure(expenditure: ExpenditureSchema): string {
	return `${expenditure.name}`;
}

export function formatDepartment(department: DepartmentSchema): string {
	if (!department) return "Не указано";
	return department.name;
}

export function formatDocument(document: DocumentSchema): string {
	return document.name;
}

export function formatDocuments(documents: Array<DocumentSchema>): string {
	return documents.map((document) => formatDocument(document)).join("\n");
}

export function formatStatus(_: any) {
	return "Не поддерживается";
}
