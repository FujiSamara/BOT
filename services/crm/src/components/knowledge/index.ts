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
	childrenCount: number;
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

	public async loadDivision(path: string) {
		await this._service.getDivision(path);
	}

	public division = computed(() => this._division.value);
	public card = computed(() => this._card.value);
}
