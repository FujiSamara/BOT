import { computed, ref, Ref } from "vue";
import { DepartmentSchema, PostSchema, WorkerSchema } from "@/types";
import EntityService from "@/services/entity";

export enum SelectType {
	MultiSelectInput,
	MonoSelectInput,
	MultiDocument,
	MonoDocument,
	Input,
}

export class BaseEntity<T> {
	protected _selectedEntities: Ref<T[]> = ref([]);

	public placeholder = "";
	public disabled: Ref<boolean> = ref(false);
	public selectedEntities = computed(() => this._selectedEntities.value);
	public completed: Ref<boolean> = ref(false);

	constructor(
		public required: boolean = false,
		placeholder?: string,
	) {
		this.sortComparator = this.sortComparator.bind(this);

		this.placeholder = placeholder || this.placeholder;
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

	protected abstract onSubmit(_: string): Promise<void>;

	public clear() {
		this._inputValue.value = "";
		this._selectedEntities.value = [];
	}

	public init(value: T) {
		this._selectedEntities.value = [value];
		this._inputValue.value = this.format(value);
	}
}

export abstract class ValidatingInputEntity<T> extends InputEntity<T> {
	public validatingResult: Ref<string> = ref("");

	constructor(required: boolean = false, placeholder?: string) {
		super(required, placeholder);
	}
}

export class FloatInputEntity extends ValidatingInputEntity<number> {
	public validatingResult: Ref<string> = computed(() => {
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
		if (this._inputValue.value === "" && this._selectedEntities.value) {
			this._inputValue.value = this.format(this._selectedEntities.value[0]);
			return;
		}
		const num = parseFloat(val);

		if (!Number.isNaN(num)) {
			this._selectedEntities.value = [num];
		}
	}
}

export abstract class InputSelectEntity<T> extends InputEntity<T> {
	protected _searchEntities: Ref<T[]> = ref([]);

	constructor(
		required: boolean = false,
		private monoMode: boolean = false,
		public neededWord: number = 3,
		placeholder?: string,
	) {
		super(required, placeholder);
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

		if (this._inputValue.value === "" && this._selectedEntities.value.length) {
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
