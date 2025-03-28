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
}

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
		);
		if (division === undefined) {
			this._division.value = undefined;
			this._card.value = undefined;
			return;
		}
		if (division.type == DivisionType.division) {
			this._card.value = undefined;
			this._division.value = division;
		} else {
			// this._card.value = division;
			this._division.value = undefined;
		}
	}

	public async searchDivisions(term: string) {
		const divisions = await this._service.findDivisions(term);

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
