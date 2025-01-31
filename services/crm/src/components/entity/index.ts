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

export abstract class BaseEntity<T> {
	protected _selectedEntities: Ref<T[]> = ref([]);
	protected _searchEntities: Ref<T[]> = ref([]);
	protected _inputValue: Ref<string> = ref("");

	constructor(
		public required: boolean = false,
		private monoMode: boolean = false,
		public neededWord: number = 3,
	) {
		this.sortComparator = this.sortComparator.bind(this);
	}

	public loading: Ref<boolean> = ref(false);
	public placeholder = "";
	public disabled: Ref<boolean> = ref(false);

	public selectedEntities = computed(() => this._selectedEntities.value);
	public entitiesList = computed((): { value: string; checked: boolean }[] => {
		const result: { value: string; checked: boolean }[] = [];

		if (!this.monoMode) {
			result.concat(
				this._selectedEntities.value.map((val) => ({
					value: this.format(val),
					checked: true,
				})),
			);
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
			await this.onInput(val);
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

	private setSelectedEntities(values: T[]) {
		this._selectedEntities.value = values.sort(this.sortComparator);
	}

	protected abstract onInput(_: string): Promise<void>;
	protected format(value: T): string {
		return `${value}`;
	}
	protected sortComparator(a: T, b: T): number {
		return this.format(a).localeCompare(this.format(b));
	}

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

		this._selectedEntities.value = [value];
		this._inputValue.value = this.format(value);
	}
	public clear() {
		this._inputValue.value = "";
		this._selectedEntities.value = [];
		this._searchEntities.value = [];
	}
}

export class DepartmentEntity extends BaseEntity<DepartmentSchema> {
	public placeholder = "Предприятие";

	protected async onInput(val: string): Promise<void> {
		const service = new EntityService<DepartmentSchema>("department");

		const departments = await service.searchEntities(val);

		this._searchEntities.value = departments.sort(this.sortComparator);
	}

	protected format(value: DepartmentSchema): string {
		return value.name;
	}
}

export class PostEntity extends BaseEntity<PostSchema> {
	public placeholder = "Должность";

	protected async onInput(val: string): Promise<void> {
		const service = new EntityService<PostSchema>("post");

		const posts = await service.searchEntities(val);

		this._searchEntities.value = posts.sort(this.sortComparator);
	}

	protected format(value: DepartmentSchema): string {
		return value.name;
	}
}

export class WorkerEntity extends BaseEntity<WorkerSchema> {
	public placeholder = "Сотрудник";

	protected async onInput(val: string): Promise<void> {
		const service = new EntityService<WorkerSchema>("worker");

		const departments = await service.searchEntities(val);

		this._searchEntities.value = departments.sort(this.sortComparator);
	}

	protected format(value: WorkerSchema): string {
		return `${value.l_name} ${value.f_name} ${value.o_name}`;
	}
}
