import { computed, ref, Ref } from "vue";

import { KnowledgeService } from "@/services/knowledge";
import { BaseSchema } from "@/types";

export interface KnowledgeDivision extends BaseSchema {
	title: string;
	filesCount: number;
	type: "card" | "chapter";
	path: string;
}

export interface KnowledgeCard extends KnowledgeDivision {
	cardType: "dish" | "common";
}

export interface KnowledgeChapter extends KnowledgeDivision {
	children: Array<KnowledgeChapter | KnowledgeCard>;
	childrenCount: number;
}

const mockDivision: KnowledgeChapter = {
	id: 1,
	type: "chapter",
	title: "Продукт",
	filesCount: 30,
	path: "product",
	childrenCount: 4,
	children: [
		{
			id: 2,
			type: "chapter",
			title: "Стандарты",
			path: "standarts",
			filesCount: 20,
			childrenCount: 2,
			children: [
				{
					id: 3,
					type: "chapter",
					title: "Фото стандарта блюд",
					path: "photos",
					filesCount: 20,
					childrenCount: 2,
					children: [
						{
							id: 7,
							type: "card",
							title: "Mac&Cheese",
							path: "maccheese",
							filesCount: 20,
							cardType: "dish",
						},
						{
							id: 8,
							type: "card",
							title: "Роллы",
							path: "rolls",
							filesCount: 20,
							cardType: "dish",
						},
						{
							id: 9,
							type: "card",
							title: "Салаты",
							path: "salads",
							filesCount: 20,
							cardType: "dish",
						},
					],
				},
				{
					id: 4,
					type: "card",
					title: "Стандарты приготовления",
					path: "cooking-standarts",
					filesCount: 20,
					cardType: "common",
				},
				{
					id: 5,
					type: "chapter",
					title: "Пособие для кухни",
					path: "kitchen",
					filesCount: 20,
					childrenCount: 3,
					children: [
						{
							id: 6,
							type: "chapter",
							title: "Test",
							path: "test",
							filesCount: 20,
							childrenCount: 0,
							children: [],
						},
					],
				},
			],
		},
	],
};

const getMockDivision = (
	path: string[],
	divisions: KnowledgeDivision[],
): KnowledgeDivision | undefined => {
	const div = divisions.find((val) => val.path === path[0]);
	if (div === undefined) return;

	if (path.length === 1) return div;
	if (div.type === "card") return;

	return getMockDivision(path.slice(1), (div as KnowledgeChapter).children);
};

export class KnowledgeController {
	private _division: Ref<KnowledgeDivision | undefined> = ref(undefined);

	private _service = new KnowledgeService();

	constructor() {}

	public async loadDivision(path: string[]) {
		this._division.value = getMockDivision(path, [mockDivision]);
	}

	public division = computed(() => this._division.value);
}
