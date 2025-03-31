import { computed, ref, Ref } from "vue";

import { KnowledgeService } from "@/services/knowledge";
import * as config from "@/config";
import { BaseSchema } from "@/types";

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

export interface DishCard extends Card {
	name: string;
	image: string;
}

//

const routerToActual = {
	product: "Продукт",
	marketing: "Маркетинг",
	purchases: "Закупки",
};

export function routerToActualPath(path: string): string {
	let result = path;
	for (const key of Object.keys(routerToActual)) {
		result = result.replace(key, (routerToActual as any)[key]);
	}
	return result;
}

export function actualToRouterPath(path: string): string {
	let result = path;
	for (const key of Object.keys(routerToActual)) {
		result = result.replace((routerToActual as any)[key], key);
	}
	return result;
}

//
export class KnowledgeController {
	private _division: Ref<KnowledgeDivision | undefined> = ref(undefined);
	private _card: Ref<Card | undefined> = ref(undefined);

	private _service: KnowledgeService;

	constructor() {
		const endpoint = `${config.knowledgeURL}/${config.knowledgeEndpoint}`;
		this._service = new KnowledgeService(endpoint);
	}

	private routerToActualPath(path: string): string {
		let result = path;
		result = result.replace("product", "Продукт");
		return result;
	}

	public async loadDivision(path: string) {
		const division = await this._service.getDivision(
			this.routerToActualPath(path),
			0,
		);
		if (division === undefined) {
			this._division.value = undefined;
			this._card.value = undefined;
			return;
		}
		this._division.value = division;
		if (division.type == DivisionType.division) {
			this._card.value = undefined;
		} else {
			const card = await this._service.getCard(division.id, division.type);
			if (card === undefined) return;
			if (division.type === DivisionType.dish) card.type = CardType.dish;
			else card.type = CardType.business;

			this._card.value = card;
		}
	}

	public async searchDivisions(term: string) {
		const divisions = await this._service.findDivisions(term, 0);

		this._division.value = {
			id: -1,
			name: "Поиск",
			filesCount: 0,
			type: DivisionType.division,
			subdivisionsCount: 0,
			path: "/search",
			subdivisions: divisions,
		};
	}

	public division = computed(() => this._division.value);
	public card = computed(() => this._card.value);
}
