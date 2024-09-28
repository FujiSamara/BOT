import {
	DepartmentSchema,
	DocumentSchema,
	ExpenditureSchema,
	PostSchema,
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
	const cellLines: Array<CellLine> = [];

	if (documents.length) {
		cellLines.push(
			...documents.map((document) => formatDocument(document).cellLines[0]),
		);
	} else {
		cellLines.push(new CellLine("Отсутствуют"));
	}

	return new Cell(...cellLines);
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

export function formatCheck(check: boolean) {
	return new Cell(new CellLine(check ? "Да" : "Нет"));
}

export function formatPost(post: PostSchema) {
	return new Cell(new CellLine(post.name));
}
