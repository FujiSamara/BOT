import { computed, ComputedRef, ref, Ref } from "vue";
import {
	DepartmentSchema,
	DocumentSchema,
	ExpenditureSchema,
	PostSchema,
	WorkerSchema,
} from "@/types";
import EntityService from "@/services/entity";
import * as parser from "@/parser";

export enum SelectType {
	MultiSelectInput,
	MonoSelectInput,
	MultiDocument,
	MonoDocument,
	Input,
	Date,
	Time,
	Checkbox,
}

export class BaseEntity<T> {
	protected _selectedEntities: Ref<T[]> = ref([]);

	public placeholder = "";
	public disabled: Ref<boolean> = ref(false);
	public completed: Ref<boolean> = ref(false);
	public selectedEntities = computed(() => this._selectedEntities.value);
	public error: ComputedRef<string | undefined> = computed(
		() => this.overrideError.value,
	);
	public overrideError: Ref<string | undefined> = ref();
	public withTitle: boolean = false;

	constructor(
		public required: boolean = false,
		placeholder?: string,
		public readonly?: boolean,
	) {
		this.sortComparator = this.sortComparator.bind(this);

		this.placeholder = placeholder || this.placeholder;
	}

	public getResult(): any {
		return this._selectedEntities.value[0];
	}

	protected format(value: T): string {
		return `${value}`;
	}
	protected sortComparator(a: T, b: T): number {
		return this.format(a).localeCompare(this.format(b));
	}
	protected setSelectedEntities(values: T[]) {
		this._selectedEntities.value = values.sort(this.sortComparator);
	}
	public init(value: T) {
		this._selectedEntities.value = [value];
	}
	public clear() {
		this._selectedEntities.value = [];
	}
}

export class BoolEntity extends BaseEntity<boolean> {
	constructor(
		placeholder?: string,
		readonly?: boolean,
		defaultValue: boolean = false,
	) {
		super(false, placeholder, readonly);

		this.checked.value = defaultValue;
		this._selectedEntities.value[0] = defaultValue;
		this.completed.value = true;
	}

	public checked = computed({
		get: () => {
			return this._selectedEntities.value[0];
		},
		set: (val) => {
			this._selectedEntities.value = [val];
		},
	});
}

export class DocumentEntity extends BaseEntity<DocumentSchema> {
	public completed = computed(() => this._selectedEntities.value.length !== 0);

	protected format(value: DocumentSchema): string {
		return value.name;
	}

	public submit(value: DocumentSchema | DocumentSchema[]) {
		if (!(value instanceof Array)) {
			value = [value];
		}
		this._selectedEntities.value = [...this._selectedEntities.value, ...value];
	}

	public init(value: DocumentSchema | DocumentSchema[]): void {
		this.submit(value);
	}

	public getResult() {
		return this._selectedEntities.value;
	}
}

export abstract class InputEntity<T> extends BaseEntity<T> {
	protected _inputValue: Ref<string> = ref("");

	public completed: Ref<boolean> = computed(() => {
		return this._selectedEntities.value.length !== 0;
	});
	public formattedField = computed({
		get: () => {
			return this._inputValue.value;
		},
		set: async (val: string) => {
			this._inputValue.value = val;
			this.onSubmit(val);
		},
	});

	protected async onSubmit(_: string): Promise<void> {}

	public clear() {
		this._inputValue.value = "";
		super.clear();
	}

	public init(value: T) {
		this._selectedEntities.value = [value];
		this._inputValue.value = this.format(value);
	}
}

export class DateEntity extends InputEntity<Date> {
	public error: ComputedRef<string | undefined> = computed(() => {
		if (this.overrideError.value !== undefined) {
			return this.overrideError.value;
		}

		if (this._inputValue.value.length === 0) {
			return "";
		}
		if (!parser.validateFormattedDate(this._inputValue.value)) {
			return "Значение должно быть в формате DD.MM.YY";
		}
		return "";
	});
	protected async onSubmit(value: string): Promise<void> {
		if (value === "") {
			this._selectedEntities.value = [];
			return;
		}
		if (parser.validateFormattedDate(value)) {
			this._selectedEntities.value = [parser.formattedDateToDate(value)];
		}
	}

	public getResult() {
		const date = this._selectedEntities.value[0];
		const formattedDate =
			date.getFullYear() +
			"-" +
			(date.getMonth() + 1).toString().padStart(2, "0") +
			"-" +
			date.getDate().toString().padStart(2, "0");

		return formattedDate;
	}

	protected format(value: Date | string): string {
		if (typeof value === "string") {
			value = new Date(value);
		}
		return parser.formatDate(value.toDateString()).cellLines[0].value;
	}

	public init(value: Date): void {
		if (value === undefined) {
			return;
		}
		const date = new Date(value);

		this._selectedEntities.value = [date];
		this._inputValue.value = this.format(value);
	}
}

export class TimeEntity extends InputEntity<Date> {
	public error: ComputedRef<string | undefined> = computed(() => {
		if (this.overrideError.value !== undefined) {
			return this.overrideError.value;
		}

		if (this._inputValue.value.length === 0) {
			return "";
		}
		if (!parser.validateFormattedTime(this._inputValue.value)) {
			return "Значение должно быть в формате HH:MM:SS";
		}
		return "";
	});
	protected async onSubmit(value: string): Promise<void> {
		if (value === "") {
			this._selectedEntities.value = [];
			return;
		}
		if (parser.validateFormattedTime(value)) {
			this._selectedEntities.value = [parser.formattedTimeToTime(value)];
		}
	}

	public getResult() {
		const date = this._selectedEntities.value[0];

		const formattedResult =
			date.getFullYear() +
			"-" +
			(date.getMonth() + 1).toString().padStart(2, "0") +
			"-" +
			date.getDate().toString().padStart(2, "0") +
			" " +
			this._inputValue.value;
		return formattedResult;
	}

	protected format(value: Date | string): string {
		if (typeof value === "string") {
			value = new Date(value);
		}
		return parser.formatTime(value.toString()).cellLines[0].value;
	}

	public init(value: Date): void {
		if (value === undefined) {
			return;
		}
		const date = new Date(value);

		this._selectedEntities.value = [date];
		this._inputValue.value = this.format(value);
	}
}

export class FloatInputEntity extends InputEntity<number> {
	public error: ComputedRef<string> = computed(() => {
		if (this.overrideError.value !== undefined) {
			return this.overrideError.value;
		}

		if (this._inputValue.value.length === 0) {
			return "";
		}
		const num = parseFloat(this._inputValue.value);
		if (Number.isNaN(num)) {
			return "Значение должно быть числом";
		}
		return "";
	});

	protected async onSubmit(val: string): Promise<void> {
		const num = parseFloat(val);

		if (!Number.isNaN(num)) {
			this._selectedEntities.value = [num];
		}
	}
}

export class StringInputEntity extends InputEntity<string> {
	public error: ComputedRef<string | undefined> = computed(() => {
		if (this.overrideError.value !== undefined) {
			return this.overrideError.value;
		}
		return;
	});

	protected async onSubmit(val: string): Promise<void> {
		this._selectedEntities.value = [val];
	}
}

export class BidStatusEntity extends StringInputEntity {
	protected format(value: string): string {
		const cell = parser.formatMultilineString(value);

		return cell.cellLines.map((line) => line.value).join(" ");
	}
}

export abstract class InputSelectEntity<T> extends InputEntity<T> {
	protected _searchEntities: Ref<T[]> = ref([]);

	constructor(
		required: boolean = false,
		private monoMode: boolean = false,
		public neededWord: number = 3,
		placeholder?: string,
		readonly?: boolean,
	) {
		super(required, placeholder, readonly);
	}

	public loading: Ref<boolean> = ref(false);

	public completed: Ref<boolean> = computed(() => {
		return this._selectedEntities.value.length !== 0;
	});
	public entitiesList = computed((): { value: string; checked: boolean }[] => {
		let result: { value: string; checked: boolean }[] = [];

		if (!this.monoMode) {
			result = this._selectedEntities.value.map((val) => ({
				value: this.format(val),
				checked: true,
			}));
		}

		for (const val of this._searchEntities.value) {
			const formatted = this.format(val);

			const found = this._selectedEntities.value.find(
				(val) => this.format(val) === formatted,
			);

			if (!found) {
				result.push({ value: formatted, checked: false });
			}
		}

		return result;
	});
	public formattedField = computed({
		get: () => {
			return this._inputValue.value;
		},
		set: async (val: string) => {
			this._inputValue.value = val;
			if (val.length < this.neededWord) {
				this._searchEntities.value = [];
				return;
			}
			this.loading.value = true;
			await this.onSubmit(val);
			this.loading.value = false;
		},
	});
	public notFound = computed(() => {
		return (
			this._inputValue.value &&
			!this.loading.value &&
			this._searchEntities.value.length === 0 &&
			this._selectedEntities.value.length === 0
		);
	});

	public remove(index: number) {
		const temp = [...this._selectedEntities.value];
		temp.splice(index, 1);
		this.setSelectedEntities(temp);
	}
	public select(index: number) {
		const el = this.entitiesList.value[index];

		if (this.monoMode) {
			this._selectedEntities.value = [this._searchEntities.value[index]];
			this.restoreSaved();
			return;
		}

		if (el.checked) {
			this.remove(index);
		} else {
			const selected = this._searchEntities.value.find(
				(val) => this.format(val) === el.value,
			);
			const temp = [...this._selectedEntities.value, selected!];
			this.setSelectedEntities(temp);
		}
	}
	public restoreSaved() {
		if (!this.monoMode) {
			throw new Error("Restoring saved must call only in monoMode.");
		}

		if (
			this._inputValue.value === "" &&
			this._selectedEntities.value.length &&
			this.neededWord !== 0
		) {
			this.remove(0);
		}

		if (this._selectedEntities.value.length) {
			const selected = this._selectedEntities.value[0];
			this._inputValue.value = this.format(selected);
			this._searchEntities.value = [];
		} else {
			this._inputValue.value = "";
			this._searchEntities.value = [];
		}
	}
	public init(value: T) {
		if (!this.monoMode) {
			throw new Error("Restoring saved must call only in monoMode.");
		}

		super.init(value);
	}
	public clear() {
		super.clear();
		this._searchEntities.value = [];
	}
}

export interface EnumRecord {
	formatted: string;
	value: string;
}

export class EnumEntity extends InputSelectEntity<EnumRecord> {
	constructor(
		protected _values: EnumRecord[],
		required: boolean = false,
		monoMode: boolean = false,
		neededWord: number = 3,
		placeholder?: string,
		readonly?: boolean,
	) {
		super(required, monoMode, neededWord, placeholder, readonly);
		if (neededWord === 0) this.onSubmit("");
	}

	protected async onSubmit(value: string): Promise<void> {
		this._searchEntities.value = this._values.filter((val) =>
			val.formatted.toLowerCase().includes(value.toLowerCase()),
		);
	}

	protected format(value: EnumRecord): string {
		return value.formatted;
	}

	public init(value: EnumRecord | string): void {
		if (typeof value === "string") {
			value = this._values.find((val) => val.value === value)!;
		}

		super.init(value);
	}

	public getResult() {
		return this._selectedEntities.value[0].value;
	}
}

export class DepartmentEntity extends InputSelectEntity<DepartmentSchema> {
	public placeholder = "Предприятие";

	protected async onSubmit(val: string): Promise<void> {
		const service = new EntityService<DepartmentSchema>("department");

		const departments = await service.searchEntities(val);

		this._searchEntities.value = departments.sort(this.sortComparator);
	}

	protected format(value: DepartmentSchema): string {
		return value.name;
	}
}

export class PostEntity extends InputSelectEntity<PostSchema> {
	public placeholder = "Должность";

	protected async onSubmit(val: string): Promise<void> {
		const service = new EntityService<PostSchema>("post");

		const posts = await service.searchEntities(val);

		this._searchEntities.value = posts.sort(this.sortComparator);
	}

	protected format(value: DepartmentSchema): string {
		return value.name;
	}
}

export class WorkerEntity extends InputSelectEntity<WorkerSchema> {
	public placeholder = "Сотрудник";

	protected async onSubmit(val: string): Promise<void> {
		const service = new EntityService<WorkerSchema>("worker");

		const departments = await service.searchEntities(val);

		this._searchEntities.value = departments.sort(this.sortComparator);
	}

	protected format(value: WorkerSchema): string {
		return `${value.l_name} ${value.f_name} ${value.o_name}`;
	}
}

export class ExpenditureEntity extends InputSelectEntity<ExpenditureSchema> {
	public placeholder = "Статья";

	protected async onSubmit(val: string): Promise<void> {
		const service = new EntityService<ExpenditureSchema>("expenditure");

		const expenditures = await service.searchEntities(val);

		this._searchEntities.value = expenditures.sort(this.sortComparator);
	}

	protected format(value: ExpenditureSchema): string {
		return value.name;
	}
}
