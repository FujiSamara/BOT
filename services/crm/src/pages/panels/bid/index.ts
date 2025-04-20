import { computed } from "vue";
import { Table } from "@/components/table";
import { BidSchema, RouteData } from "@/types";
import * as parser from "@/parser";
import {
	EntitySearchModelOut,
	SearchModelOut,
	useEntitySearch,
	useSearch,
} from "@/hooks/tableSearchHook";
import {
	DateIntervalModelOut,
	useDateInterval,
} from "@/hooks/dateIntervalHook";
import { RowEditor, useRowEditor } from "@/hooks/rowEditorHook";
import {
	BidStatusEntity,
	BoolEntity,
	DateEntity,
	DepartmentEntity,
	DocumentEntity,
	EnumEntity,
	ExpenditureEntity,
	FloatInputEntity,
	SelectType,
	StringInputEntity,
	WorkerEntity,
} from "@/components/entity";
import {
	filterBidByStatus,
	BidState,
} from "@/pages/panels/bid/bidStatusFilter";
import { toast } from "vue3-toastify";
import { BidPathOptions, BidService } from "@/services/entity";

interface BidPanelData {
	searchList: SearchModelOut[];
	entitySearchList: EntitySearchModelOut;
	dateInterval: DateIntervalModelOut;
	rowEditor: RowEditor<BidSchema, BidTable>;
}

// Bid
export class BidTable extends Table<BidSchema> {
	protected _pathOptions: BidPathOptions = new BidPathOptions();
	protected _service: BidService;

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

		this._pathOptions.approveExtraPath =
			options && options.approveEndpoint ? options.approveEndpoint : "";
		this._pathOptions.rejectExtraPath =
			options && options.rejectEndpoint ? options.rejectEndpoint : "";

		this._service = new BidService("bid", this._pathOptions);

		this._formatters.set("department", parser.formatDepartment);
		this._formatters.set("worker", parser.formatWorker);
		this._formatters.set("create_date", parser.formatDate);
		this._formatters.set("close_date", parser.formatDate);
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
		await this._service
			.createEntity(model)
			.then(() => {
				this.forceRefresh();
			})
			.catch(() => {
				toast.error("Запись создалась с ошибкой.");
			});
	}

	public orderDisabled(header: string): boolean {
		return ["Документы", "Статус"].includes(header);
	}

	public async approve(
		index: number,
		needRefresh: boolean = false,
	): Promise<void> {
		await this._service
			.approveBid(this._loadedRows.value[index].id)
			.then(() => {
				if (needRefresh) {
					this.forceRefresh();
				}
			})
			.catch(() => {
				toast.error("Заявка согласована с ошибкой.");
			});
	}

	public async reject(
		index: number,
		needRefresh: boolean = false,
		reason: string,
	): Promise<void> {
		await this._service
			.rejectBid(this._loadedRows.value[index].id, reason)
			.then(() => {
				if (needRefresh) {
					this.forceRefresh();
				}
			})
			.catch(() => {
				toast.error("Заявка отклонена с ошибкой.");
			});
	}
}
export async function setupBid(
	table: BidTable,
	routeData: RouteData,
): Promise<BidPanelData> {
	const searchList = await useSearch(table, routeData, {
		schemas: [
			{
				pattern: "worker",
				groups: [0],
			},
			{
				pattern: "id",
				groups: [1],
			},
			{
				pattern: "amount",
				groups: [2],
			},
		],
		placeholder: "Поиск",
		style: "height: 100%; width: 170px",
		name: "general",
	});
	const entitySearchList = await useEntitySearch(
		table,
		routeData,
		{
			entity: new DepartmentEntity(),
			pattern: "department",
			groups: [0],
			id: 0,
		},
		{
			entity: new ExpenditureEntity(),
			pattern: "expenditure",
			groups: [1],
			id: 1,
		},
		{
			entity: new EnumEntity(
				[
					{ value: BidState.Fac, formatted: "Согласование ЦФО" },
					{ value: BidState.CC, formatted: "Согласование ЦЗ" },
					{ value: BidState.Paralegal, formatted: "Согласование ЮК" },
					{ value: BidState.KRU, formatted: "Согласование КРУ" },
					{
						value: BidState.FinancialDirectorPending,
						formatted: "Согласование финансовый директор",
					},
					{ value: BidState.TellerPending, formatted: "Согласование кассир" },
					{ value: BidState.TellerApproved, formatted: "Выплачена" },
					{ value: BidState.Denied, formatted: "Отклонена" },
				],
				false,
				false,
				0,
				"Статус",
			),
			pattern: "",
			groups: [2],
			id: 2,
			filter: filterBidByStatus,
		},
	);
	const dateInterval = await useDateInterval(table, "create_date", routeData);
	const rowEditor = useRowEditor(
		table,
		[
			{
				entity: new FloatInputEntity(true, "Сумма"),
				type: SelectType.Input,
				name: "amount",
			},
			{
				entity: new EnumEntity(
					[
						{ value: "card", formatted: "Безналичная" },
						{ value: "cash", formatted: "Наличная" },
						{ value: "taxi", formatted: "Требуется такси" },
					],
					true,
					true,
					0,
					"Тип оплаты",
				),
				type: SelectType.MonoSelectInput,
				name: "payment_type",
			},
			{
				entity: new ExpenditureEntity(true, true),
				type: SelectType.MonoSelectInput,
				name: "expenditure",
			},
			{
				entity: new BoolEntity("Счет в ЭДО"),
				type: SelectType.Checkbox,
				name: "need_edm",
			},
			{
				entity: new DepartmentEntity(true, true),
				type: SelectType.MonoSelectInput,
				name: "department",
			},
			{
				entity: new WorkerEntity(false, true, 3, "Сотрудник", true),
				type: SelectType.MonoSelectInput,
				name: "worker",
			},
			{
				entity: new StringInputEntity(true, "Цель"),
				type: SelectType.Input,
				name: "purpose",
			},
			{
				entity: new DateEntity(false, "Дата создания", true),
				type: SelectType.Date,
				name: "create_date",
			},
			{
				entity: new DateEntity(false, "Дата закрытия", true),
				type: SelectType.Date,
				name: "close_date",
			},
			// Documents
			{
				entity: new BidStatusEntity(false, "Статус", true),
				type: SelectType.Input,
				name: "status",
			},
			{
				entity: new EnumEntity(
					[
						{ value: "Текущая", formatted: "Текущая" },
						{ value: "Инвестиционная", formatted: "Инвестиционная" },
					],
					true,
					true,
					0,
					"Тип деятельности",
				),
				type: SelectType.MonoSelectInput,
				name: "activity_type",
			},
			{
				entity: new DocumentEntity(true, "Документы"),
				type: SelectType.MultiDocument,
				name: "documents",
			},
			{
				entity: new StringInputEntity(false, "Комментарий"),
				type: SelectType.Input,
				name: "comment",
			},
		],
		"Создать заявку",
		(model: BidSchema) => `Заявка №${model.id}`,
	);

	return {
		entitySearchList,
		searchList,
		dateInterval,
		rowEditor,
	};
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
