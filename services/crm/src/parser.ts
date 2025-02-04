import {
	DepartmentSchema,
	DocumentSchema,
	ExpenditureSchema,
	PostSchema,
	WorkerSchema,
} from "@types";
import * as config from "@/config";
import { Cell, CellLine } from "@/components/table";

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
		date.getDate().toString().padStart(2, "0") +
		"." +
		(date.getMonth() + 1).toString().padStart(2, "0") +
		"." +
		date.getFullYear() +
		" " +
		date.getHours().toString().padStart(2, "0") +
		":" +
		date.getMinutes().toString().padStart(2, "0") +
		":" +
		date.getSeconds().toString().padStart(2, "0");
	return new Cell(new CellLine(formattedDate));
}

export function validateDate(dateString: string): boolean {
	// First check for the pattern
	if (!/^\d{1,2}\.\d{1,2}\.\d{4}$/.test(dateString)) return false;

	// Parse the date parts to integers
	var parts = dateString.split(".");
	var day = parseInt(parts[0], 10);
	var month = parseInt(parts[1], 10);
	var year = parseInt(parts[2], 10);

	// Check the ranges of month and year
	if (year < 1000 || year > 3000 || month == 0 || month > 12) return false;

	var monthLength = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

	// Adjust for leap years
	if (year % 400 == 0 || (year % 100 != 0 && year % 4 == 0))
		monthLength[1] = 29;

	// Check the range of the day
	return day > 0 && day <= monthLength[month - 1];
}

export function formattedDateToDate(dateString: string): Date {
	const parts = dateString.split(".").map((val) => parseInt(val));

	const newString = `${parts[1]}.${parts[0]}.${parts[2]}`;
	const date = new Date(newString);

	return date;
}

export function formatDate(dateString: string): Cell {
	if (!dateString) {
		return new Cell(new CellLine());
	}

	const date = new Date(dateString);
	const formattedDate =
		date.getDate().toString().padStart(2, "0") +
		"." +
		(date.getMonth() + 1).toString().padStart(2, "0") +
		"." +
		date.getFullYear();
	return new Cell(new CellLine(formattedDate));
}

export function formatTime(dateString: string): Cell {
	if (!dateString) {
		return new Cell(new CellLine());
	}

	const date = new Date(dateString);
	const formattedDate =
		date.getHours().toString().padStart(2, "0") +
		":" +
		date.getMinutes().toString().padStart(2, "0") +
		":" +
		date.getSeconds().toString().padStart(2, "0");

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

export function capitalize(val: string) {
	return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

export function formatFloat(val: number): Cell {
	if (!val) {
		return new Cell(new CellLine("0"));
	}
	return new Cell(new CellLine(val.toFixed(2).toString()));
}
