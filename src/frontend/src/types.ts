import { computed, ref, Ref, ShallowRef } from "vue";

export interface NavigationData {
	id: number;
	imageSrc: string;
	label: string;
	isActive: boolean;
}

export enum Access {
	Bid,
	Expenditure,
}

export interface PanelData extends NavigationData {
	panel: ShallowRef<any>;
	access: Access;
}

class TableElementObserver<T> {
	constructor(
		private _element: T,
		private _elementID: number,
		private _callback: (elementID: number, newValue: T) => void,
	) {}

	get value() {
		return this._element;
	}

	set value(newValue: T) {
		this._element = newValue;
		this._callback(this._elementID, newValue);
	}
}

export class Table {
	private _highlighted: Array<boolean> = [];
	private _checked: Array<boolean> = [];
	/**  Key - ID, Value - index in internal arrays. */
	private _indexes: Map<number, number> = new Map();
	private _nextID: number = 0;
	private _content: Ref<Array<{ id: number; columns: Array<string> }>> = ref(
		[],
	);

	/**
	 * @param tableContent
	 * @param _searchColumnIndexes Indexes of columns for searching.
	 */
	constructor(
		tableContent: Array<Array<string>>,
		private _searchColumnIndexes: Array<number> = [],
	) {
		for (const columnIndex of _searchColumnIndexes) {
			if (columnIndex < 0 || columnIndex >= tableContent[0].length) {
				throw new Error(`Invalid column index: ${columnIndex}`);
			}
		}

		for (let index = 0; index < tableContent.length; index++) {
			const row = tableContent[index];
			this.push(row);
		}
	}

	private elementChecked(id: number, newValue: boolean): void {
		const curIndex = this._indexes.get(id)!;
		this._checked[curIndex] = newValue;
		this._content.value[curIndex].id = this._nextID;
		this._indexes.delete(id);
		this._indexes.set(this._nextID, curIndex);
		this._nextID++;
	}
	private elementHighlighted(id: number, newValue: boolean): void {
		const curIndex = this._indexes.get(id)!;
		this._highlighted[curIndex] = newValue;
		this._content.value[curIndex].id = this._nextID;
		this._indexes.delete(id);
		this._indexes.set(this._nextID, curIndex);
		this._nextID++;
	}

	private _searchedRows = computed(() => {
		const searchResult: Array<{ id: number; columns: Array<string> }> = [];

		for (let index = 0; index < this._content.value.length; index++) {
			const columns = this._content.value[index];

			for (const columnIndex of this._searchColumnIndexes) {
				const searchString = this.searchString.value.toLowerCase();
				const talbeElement = columns.columns[columnIndex].toLowerCase();
				if (talbeElement.indexOf(searchString) !== -1) {
					searchResult.push(columns);
					break;
				}
			}
		}

		return searchResult;
	});

	private _filteredRows = computed(() => {
		const filterResult: Array<{ id: number; columns: Array<string> }> =
			this._searchedRows.value.filter(
				(row: { id: number; columns: Array<string> }) => {
					for (const filter of this.filters.value) {
						if (!filter(row)) return false;
					}
					return true;
				},
			);

		return filterResult;
	});

	// Public fields
	public searchString: Ref<string> = ref("");
	/** Filters for rows. Must returns **true** if row need be shown. */
	public filters: Ref<
		Array<(row: { id: number; columns: Array<string> }) => boolean>
	> = ref([]);

	public data = computed(() => {
		return this._filteredRows.value;
	});

	public isChecked(id: number): TableElementObserver<boolean> {
		return new TableElementObserver(
			this._checked[this._indexes.get(id)!],
			id,
			this.elementChecked.bind(this),
		);
	}

	public isHighlighted(id: number): TableElementObserver<boolean> {
		return new TableElementObserver(
			this._highlighted[this._indexes.get(id)!],
			id,
			this.elementHighlighted.bind(this),
		);
	}

	public isAnyChecked(): boolean {
		for (let index = 0; index < this._checked.length; index++) {
			if (this._checked[index]) return true;
		}
		return false;
	}

	public push(row: Array<string>): void {
		this._content.value.push({ columns: row, id: this._nextID });
		this._indexes.set(this._nextID, this._checked.length);
		this._checked.push(false);
		this._highlighted.push(false);
		this._nextID++;
	}

	public erase(id: number): void {
		const deleteIndex = this._indexes.get(id)!;
		if (!this._indexes.delete(id)) throw new Error(`ID ${id} not exist`);
		this._checked.splice(deleteIndex, 1);
		this._highlighted.splice(deleteIndex, 1);
		this._content.value.splice(deleteIndex, 1);
		for (let index = deleteIndex; index < this._content.value.length; index++) {
			const element = this._content.value[index];
			this._indexes.set(element.id, this._indexes.get(element.id)! - 1);
		}
	}

	public deleteChecked(): void {
		for (let index = 0; index < this._content.value.length; index++) {
			const id = this._content.value[index].id;

			if (this._checked[index]) {
				this.erase(id);
				index--;
			}
		}
	}
}
