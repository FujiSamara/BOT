import { computed, ref, Ref } from "vue";
import { DepartmentSchema } from "@/types";
import EntityService from "@/services/entity";

export class BaseEntity<T> {
	protected _selectedEntity: Ref<T | undefined> = ref();
	protected _searchEntities: Ref<T[]> = ref([]);
	protected _inputValue: Ref<string> = ref("");

	constructor() {}

	public disabled: Ref<boolean> = ref(false);
	public get selectedEntity() {
		return this._selectedEntity.value;
	}

	public entitiesList = computed(() => {
		return this._searchEntities.value.map((val) => this.format(val));
	});
	public formattedField = computed({
		get: () => {
			return this._inputValue.value;
		},
		set: async (val: string) => {
			await this.search(val);
		},
	});

	protected async search(val: string) {}

	protected format(value: any): string {
		return `${value}`;
	}

	public clear() {
		this._selectedEntity.value = undefined;
		this._inputValue.value = "";
	}
}

export class DepartmentEntity extends BaseEntity<DepartmentSchema> {
	protected async search(val: string): Promise<void> {
		const service = new EntityService("department");
	}
}
