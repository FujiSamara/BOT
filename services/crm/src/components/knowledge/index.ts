import { computed, ref, Ref } from "vue";

import { KnowledgeService } from "@/services/knowledge";
import * as config from "@/config";
import { BaseSchema, PanelData } from "@/types";
import { useNetworkStore } from "@/store/network";
import { getKnowledgeByAccesses } from "@/pages/panels";

export enum CardType {
	dish = "dish",
	business = "business",
}

export enum DivisionType {
	division = "division",
	dish = "dish",
	business = "business",
}

export interface KnowledgeSubdivision extends BaseSchema {
	name: string;
	filesCount: number;
	type: DivisionType;
	subdivisionsCount: number;
	path: string;
}

export interface KnowledgeDivision extends KnowledgeSubdivision {
	subdivisions: KnowledgeSubdivision[];
}

export interface Card extends BaseSchema {
	name: string;
	type: CardType;
}

export interface BusinessCard extends Card {
	name: string;
	description: string | undefined;
	materials: [];
}

interface IngredientSchema extends BaseSchema {
	id: number;
	title: string;
	amount: number;
}
export interface DishModifierSchema extends BaseSchema {
	title: string;
	ingredients: IngredientSchema[];
}

export interface FileLinkSchema extends BaseSchema {
	url: string;
	name: string;
	size: number;
	created: string;
}

export interface DishMaterials {
	video?: FileLinkSchema;
	materials: FileLinkSchema[];
}

export interface DishCard extends Card {
	name: string;
	image: string;
	description: string;
	modifiers?: DishModifierSchema[];
	materials?: DishMaterials;
}

//

const routerToActual = {
	product: "Продукт",
	marketing: "Маркетинг",
	staff: "Персонал",
	purchases: "Закупки",
	cd: "ЦД",
	control: "Контроль",
	accounting: "Учет",
};

export function routerToActualPath(path: string): string {
	let result = path;
	for (const key of Object.keys(routerToActual)) {
		result = result.replace(key, (routerToActual as any)[key]);
	}
	result = result.replace("+", "%2B").replace("&", "%26");
	return result;
}

export function actualToRouterPath(path: string): string {
	let result = path;
	for (const key of Object.keys(routerToActual)) {
		result = result.replace((routerToActual as any)[key], key);
	}
	result = result.replace("%2B", "+").replace("%26", "&");
	return result;
}

export const DIVISION_CHUNK_SIZE = 50;

//
export class KnowledgeController {
	private _division: Ref<KnowledgeDivision | undefined> = ref(undefined);
	public lastDivisionPage = ref(false);
	private _subdivisionsPage = 0;

	private _card: Ref<Card | undefined> = ref(undefined);

	private _service: KnowledgeService;

	public divisionLoading = ref(false);
	public divisionExtending = ref(false);

	constructor() {
		const endpoint = `${config.knowledgeURL}/${config.knowledgeEndpoint}`;
		this._service = new KnowledgeService(endpoint);
	}

	private async loadCard() {
		const division = this._division.value!;

		const card = await this._service.getCard(division.id, division.type);

		if (card === undefined) return;
		if (division.type === DivisionType.dish) card.type = CardType.dish;
		else card.type = CardType.business;

		this._card.value = card;
		this.divisionLoading.value = false;

		if (division.type === DivisionType.dish) {
			this._service.getDishModifiers(card.id).then((val) => {
				const fullCard: DishCard = {
					...(this._card.value as any),
					modifiers: val,
				};

				this._card.value = fullCard;
			});
			this._service.getDishMaterials(card.id).then((val) => {
				const fullCard: DishCard = {
					...(this._card.value as any),
					materials: val,
				};

				this._card.value = fullCard;
			});
		}
	}

	// Load
	public async loadDivision(path: string) {
		this.divisionLoading.value = true;
		this._subdivisionsPage = 1;
		this._division.value = undefined;
		this._card.value = undefined;
		const division = await this._service.getDivision(path, 0);
		if (division === undefined) {
			this.divisionLoading.value = false;
			return;
		}
		this._division.value = division;
		this.divisionLoading.value = false;
		if (division.type == DivisionType.division) {
			this._card.value = undefined;
			this.lastDivisionPage.value =
				division.subdivisionsCount < DIVISION_CHUNK_SIZE;
			this.divisionLoading.value = false;
		} else {
			await this.loadCard();
		}
	}
	public async nextSubdivisions() {
		if (this._division.value === undefined) return;

		this.divisionExtending.value = true;
		const division = await this._service.getDivision(
			this._division.value.path,
			this._subdivisionsPage * DIVISION_CHUNK_SIZE,
		);
		if (division === undefined) {
			this.divisionExtending.value = false;
			return;
		}

		this.lastDivisionPage.value =
			division.subdivisionsCount < DIVISION_CHUNK_SIZE;

		this._division.value = {
			...this._division.value,
			subdivisions: [
				...this._division.value.subdivisions,
				...division.subdivisions,
			],
		};

		this._subdivisionsPage += 1;
		this.divisionExtending.value = false;
	}

	// Search
	public async searchDivisions(term: string) {
		this.divisionLoading.value = true;
		this._subdivisionsPage = 1;
		const divisions = await this._service.findDivisions(term, 0);

		this.lastDivisionPage.value = divisions.length < DIVISION_CHUNK_SIZE;

		this._division.value = {
			id: -1,
			name: "Поиск",
			filesCount: 0,
			type: DivisionType.division,
			subdivisionsCount: divisions.length,
			path: "Результаты поиска",
			subdivisions: divisions,
		};
		this.divisionLoading.value = false;
	}
	public async nextSearchingResults(term: string) {
		if (this._division.value === undefined) return;

		this.divisionLoading.value = true;
		const divisions = await this._service.findDivisions(
			term,
			this._subdivisionsPage * DIVISION_CHUNK_SIZE,
		);
		this.lastDivisionPage.value = divisions.length < DIVISION_CHUNK_SIZE;

		this._division.value = {
			...this._division.value,
			subdivisions: [...this._division.value.subdivisions, ...divisions],
		};

		this._subdivisionsPage += 1;
		this.divisionLoading.value = false;
	}

	public division = computed(() => {
		if (this._division.value === undefined) return;

		const networkStore = useNetworkStore();
		const knowledgePanels = getKnowledgeByAccesses(networkStore.accesses);

		return {
			...this._division.value,
			subdivisions: this._division.value.subdivisions.filter((sub) =>
				this.haveAccessToDivision(sub.path, knowledgePanels),
			),
		};
	});
	public card = computed(() => this._card.value);

	private haveAccessToDivision(
		path: string,
		knowledgePanels: PanelData[],
	): boolean {
		const routerPath = actualToRouterPath(path);
		const name = routerPath.split("/")[1];

		return knowledgePanels.find((val) => val.name === name) !== undefined;
	}
}
