import { computed, ref, Ref } from "vue";

import { KnowledgeService } from "@/services/knowledge";
import { BaseSchema } from "@/types";

export interface KnowledgeDivision extends BaseSchema {
	title: string;
	filesCount: number;
	type: "card" | "chapter";
	path: string;
}

export interface KnowledgeCard extends KnowledgeDivision {}

export interface KnowledgeChapter extends KnowledgeDivision {
	children: Array<KnowledgeChapter | KnowledgeCard>;
	childrenCount: number;
}

export class KnowledgeController {
	private _division: Ref<KnowledgeDivision | undefined> = ref(undefined);

	private _service = new KnowledgeService();

	constructor() {}

	public async loadDivision(path: string[]) {
		const children = [
			{
				id: 1,
				type: "chapter",
				title: "Фото стандарты блюд",
				children: [
					{
						id: 1,
						type: "chapter",
						title: "Фото стандарты блюд",
						children: [],
						path: "",
						filesCount: 20,
						childrenCount: 3,
					},
					{
						id: 1,
						type: "card",
						title: "Test_2",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Test_2",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Test_2",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Test_2",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Test_2",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Test_2",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
					{
						id: 1,
						type: "card",
						title: "Тест",
						filesCount: 20,
					},
				],
				path: "",
				filesCount: 20,
				childrenCount: 3,
			},
		];

		this._division.value = {
			id: 1,
			type: "chapter",
			title: "Стандарты",
			filesCount: 20,
			path: "Продукт / Стандарты",
			children: [...children, ...children, ...children],
			childrenCount: 2,
		} as KnowledgeChapter;
	}

	public division = computed(() => this._division.value);
}
