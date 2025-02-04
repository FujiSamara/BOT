import {
	DepartmentSchema,
	DocumentSchema,
	ExpenditureSchema,
	PostSchema,
	WorkerSchema,
} from "@/types";
import * as config from "@/config";
import { Cell, CellLine } from "@/table";

export function formatWorker(worker: WorkerSchema): Cell {
	if (!worker) return new Cell();
	return new Cell(
		new CellLine(`${worker.l_name} ${worker.f_name} ${worker.o_name}`),
	);
}

export function formatDateTime(dateString: string): Cell {
	if (!dateString) {
		return new Cell(new CellLine());
	}

	const date = new Date(dateString);
	const formattedDate =
		date.getFullYear() +
		"-" +
		(date.getMonth() + 1).toString().padStart(2, "0") +
		"-" +
		date.getDate().toString().padStart(2, "0") +
		" " +
		date.getHours().toString().padStart(2, "0") +
		":" +
		date.getMinutes().toString().padStart(2, "0") +
		":" +
		date.getSeconds().toString().padStart(2, "0");
	return new Cell(new CellLine(formattedDate));
}

export function formatDate(dateString: string): Cell {
	if (!dateString) {
		return new Cell(new CellLine());
	}

	const date = new Date(dateString);
	const formattedDate =
		date.getFullYear() +
		"-" +
		(date.getMonth() + 1).toString().padStart(2, "0") +
		"-" +
		date.getDate().toString().padStart(2, "0");
	return new Cell(new CellLine(formattedDate));
}

export function formatExpenditure(expenditure: ExpenditureSchema): Cell {
	return new Cell(new CellLine(expenditure.name));
}

export function formatDepartment(department: DepartmentSchema): Cell {
	if (!department) return new Cell();
	return new Cell(new CellLine(department.name));
}

export function formatDocument(document: DocumentSchema): Cell {
	return new Cell(
		new CellLine(
			document.name,
			document.href,
			undefined,
			Boolean(document.forceHref),
		),
	);
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
	if (!post) {
		return new Cell(new CellLine("Отсутствует"));
	}
	return new Cell(new CellLine(post.name));
}

export function formatWorkTimePhoto(photoID: string): Cell {
	if (!photoID) {
		return new Cell(new CellLine("Отсутствует"));
	}
	const href = `${config.fullBackendURL}/${config.crmEndpoint}/worktime/download_photo/${photoID}`;

	return new Cell(new CellLine(`photo_${photoID}.jpg`, href, undefined, true));
}

export function formatMultilineString(multilineString: string): Cell {
	const multilines: Array<string> = multilineString.split("/next/");
	const cellLines: Array<CellLine> = [];

	const colors = [undefined, "#1a11d1", "#d1c111"];
	let currentColorIndex = 0;

	for (const multiline of multilines) {
		cellLines.push(
			...multiline
				.split("\n")
				.map((val) => new CellLine(val, undefined, colors[currentColorIndex])),
		);
		currentColorIndex++;
		currentColorIndex %= colors.length;
	}

	return new Cell(...cellLines);
}
