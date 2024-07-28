import {
	DepartmentSchema,
	DocumentSchema,
	ExpenditureSchema,
	WorkerSchema,
} from "@/types";
import { Cell, CellLine } from "@/table";

export function formatWorker(worker: WorkerSchema): Cell {
	if (!worker) return new Cell();
	return new Cell(
		new CellLine(`${worker.l_name} ${worker.f_name} ${worker.o_name}`),
	);
}

export function formatDate(dateString: string): Cell {
	const date = new Date(dateString);
	return new Cell(new CellLine(date.toLocaleString()));
}

export function formatExpenditure(expenditure: ExpenditureSchema): Cell {
	return new Cell(new CellLine(expenditure.name));
}

export function formatDepartment(department: DepartmentSchema): Cell {
	if (!department) return new Cell();
	return new Cell(new CellLine(department.name));
}

export function formatDocument(document: DocumentSchema): Cell {
	return new Cell(new CellLine(document.name, document.href));
}

export function formatDocuments(documents: Array<DocumentSchema>): Cell {
	return new Cell(
		...documents.map((document) => formatDocument(document).cellLines[0]),
	);
}

export function formatStatus(_: Cell) {
	return new Cell(new CellLine("Временно не поддерживается"));
}

export function formatPaymentType(payment_type: string) {
	let result: string = "";

	switch (payment_type) {
		case "cash":
			result = "Наличная";
			break;
		case "card":
			result = "Безналичная";
			break;
		case "taxi":
			result = "Требуется такси";
			break;
	}

	return new Cell(new CellLine(result));
}
