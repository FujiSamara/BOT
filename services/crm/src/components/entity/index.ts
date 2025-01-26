import { computed, ref, Ref } from "vue";
import { DepartmentSchema } from "@/types";
import EntityService from "@/services/entity";

export abstract class BaseEntity<T> {
	protected _selectedEntities: Ref<T[]> = ref([]);
	protected _searchEntities: Ref<T[]> = ref([]);
	protected _inputValue: Ref<string> = ref("");

	constructor() {}

	public disabled: Ref<boolean> = ref(false);
	public get selectedEntity() {
		return this._selectedEntities.value;
	}

	public entitiesList = computed((): { value: string; checked: boolean }[] => {
		const result = this._selectedEntities.value.map((val) => ({
			value: this.format(val),
			checked: true,
		}));

		for (const val of this._searchEntities.value) {
			const formatted = this.format(val);

			if (!result.find((val) => val.value === formatted)) {
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
			await this.onInput(val);
		},
	});

	private setSelectedEntities(values: T[]) {
		this._selectedEntities.value = values.sort((a, b) =>
			this.format(a).localeCompare(this.format(b)),
		);
	}

	protected abstract onInput(_: string): Promise<void>;

	protected format(value: T): string {
		return `${value}`;
	}

	public remove(index: number) {
		const temp = [...this._selectedEntities.value];
		temp.splice(index, 1);
		this.setSelectedEntities(temp);
	}

	public select(index: number) {
		const el = this.entitiesList.value[index];

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
}

export class DepartmentEntity extends BaseEntity<DepartmentSchema> {
	protected async onInput(val: string): Promise<void> {
		if (val.length < 3) {
			this._searchEntities.value = [];
			return;
		}

		const service = new EntityService("department");

		const departments = await service.searchDepartments(val);

		this._searchEntities.value = departments.sort((a, b) =>
			a.name.localeCompare(b.name),
		);
	}

	protected format(value: DepartmentSchema): string {
		return value.name;
	}
}
