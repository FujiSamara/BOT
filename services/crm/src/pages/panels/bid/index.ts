import axios from "axios";
import { computed } from "vue";
import { Table } from "@/components/table";
import { BidSchema } from "@/types";
import { Editor } from "@/components/table/editor";
import {
	BoolSmartField,
	DepartmentSmartField,
	DocumentSmartField,
	EnumSmartField,
	ExpenditureSmartField,
	InputSmartField,
} from "@/components/table/field";
import * as parser from "@/parser";

export class BidTable extends Table<BidSchema> {
	constructor(options?: {
		getEndpoint?: string;
		infoEndpoint?: string;
		createEndpoint?: string;
		updateEndpoint?: string;
		deleteEndpoint?: string;
		approveEndpoint?: string;
		rejectEndpoint?: string;
		exportEndpoint?: string;
	}) {
		super("bid", options);

		this._formatters.set("department", parser.formatDepartment);
		this._formatters.set("worker", parser.formatWorker);
		this._formatters.set("create_date", parser.formatDateTime);
		this._formatters.set("close_date", parser.formatDateTime);
		this._formatters.set("documents", parser.formatDocuments);
		this._formatters.set("payment_type", parser.formatPaymentType);
		this._formatters.set("expenditure", parser.formatExpenditure);
		this._formatters.set("need_edm", parser.formatCheck);
		this._formatters.set("status", parser.formatMultilineString);

		this._aliases.set("id", "ID");
		this._aliases.set("amount", "Сумма");
		this._aliases.set("payment_type", "Тип оплаты");
		this._aliases.set("department", "Производство");
		this._aliases.set("worker", "Работник");
		this._aliases.set("purpose", "Цель");
		this._aliases.set("create_date", "Дата создания");
		this._aliases.set("close_date", "Дата закрытия");
		this._aliases.set("status", "Статус");
		this._aliases.set("comment", "Комментарий");
		this._aliases.set("denying_reason", "Причина отказа");
		this._aliases.set("documents", "Документы");
		this._aliases.set("expenditure", "Статья");
		this._aliases.set("need_edm", "Счет в ЭДО");
		this._aliases.set("activity_type", "Тип деятельности");

		this._columsOrder.set("id", 0);
		this._columsOrder.set("worker", 1);
		this._columsOrder.set("expenditure", 2);
		this._columsOrder.set("amount", 3);
		this._columsOrder.set("department", 4);
		this._columsOrder.set("purpose", 5);
		this._columsOrder.set("documents", 6);
		this._columsOrder.set("status", 7);
		this._columsOrder.set("comment", 8);
		this._columsOrder.set("payment_type", 9);
		this._columsOrder.set("need_edm", 10);
		this._columsOrder.set("denying_reason", 11);
		this._columsOrder.set("create_date", 12);
		this._columsOrder.set("close_date", 13);
		this._columsOrder.set("activity_type", 14);
	}

	protected color(model: BidSchema): string {
		if (model.status.indexOf("Выплачено") !== -1) {
			return "#c8fac9";
		}
		if (model.status.indexOf("Отказано") !== -1) {
			return "#fac8ca";
		}
		return "#ffffff";
	}

	public async create(model: BidSchema): Promise<void> {
		const data = new FormData();
		model.documents.map((doc) => data.append("files", doc.file!, doc.name));

		const resp = await this._network.withAuthChecking(
			axios.post(`${this._endpoint}${this._createEndpoint}/`, model),
		);

		await this._network.withAuthChecking(
			axios.post(`${this._endpoint}/${resp.data.id}`, data, {
				headers: {
					"Content-Type": `multipart/form-data`,
				},
			}),
		);

		this.forceRefresh();
	}
}
export class FACAndCCBidTable extends BidTable {
	constructor() {
		super({
			getEndpoint: "/fac_cc",
			infoEndpoint: "/fac_cc",
			exportEndpoint: "/fac_cc",
			approveEndpoint: "/fac_cc",
			rejectEndpoint: "/fac_cc",
		});
	}

	notifies = computed(() => {
		return this.rowCount.value;
	});
}
export class FACAndCCBidHistoryTable extends BidTable {
	constructor() {
		super({
			getEndpoint: "/fac_cc/history",
			infoEndpoint: "/fac_cc/history",
			exportEndpoint: "/fac_cc/history",
			approveEndpoint: "/fac_cc/history",
			rejectEndpoint: "/fac_cc/history",
		});
	}
}
export class ParalegalBidTable extends BidTable {
	constructor() {
		super({
			getEndpoint: "/paralegal",
			infoEndpoint: "/paralegal",
			exportEndpoint: "/paralegal",
			approveEndpoint: "/paralegal",
			rejectEndpoint: "/paralegal",
		});
	}
	notifies = computed(() => {
		return this.rowCount.value;
	});
}
export class AccountantCardBidTable extends BidTable {
	constructor() {
		super({
			getEndpoint: "/accountant_card",
			infoEndpoint: "/accountant_card",
			exportEndpoint: "/accountant_card",
			approveEndpoint: "/accountant_card",
			rejectEndpoint: "/accountant_card",
		});
	}
	notifies = computed(() => {
		return this.rowCount.value;
	});
}
export class MyBidTable extends BidTable {
	constructor() {
		super({
			getEndpoint: "/my",
			infoEndpoint: "/my",
			exportEndpoint: "/my",
			createEndpoint: "",
		});
	}
}
export class ArchiveBidTable extends BidTable {
	constructor() {
		super({
			getEndpoint: "/archive",
			infoEndpoint: "/archive",
			exportEndpoint: "/archive",
			approveEndpoint: "/archive",
			rejectEndpoint: "/archive",
		});
	}
}

export class BidEditor extends Editor {
	constructor(_instance?: any) {
		super();

		this.fields = [
			new InputSmartField("Cумма", "amount", undefined, true, true),
			new EnumSmartField(
				"Тип оплаты",
				"payment_type",
				["cash", "card", "taxi"],
				undefined,
				true,
				(val) => {
					switch (val) {
						case "cash":
							return "Наличная";
						case "card":
							return "Безналичная";
						case "taxi":
							return "Требуется такси";
					}
					return val;
				},
				true,
			),
			new ExpenditureSmartField(
				"Статья",
				"expenditure",
				undefined,
				true,
				undefined,
				true,
			),
			new BoolSmartField("Счет в ЭДО", "need_edm", "Нет"),
			new DepartmentSmartField(
				"Производство",
				"department",
				undefined,
				true,
				true,
			),
			new InputSmartField("Цель", "purpose", undefined, true, true),
			new EnumSmartField(
				"Тип деятельности",
				"activity_type",
				["Инвестиционная", "Текущая"],
				undefined,
				true,
				undefined,
				true,
			),
			new DocumentSmartField("Документы", "documents", undefined, true),
			new InputSmartField("Комментарий", "comment"),
		];
	}
}
