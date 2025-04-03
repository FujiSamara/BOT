import { BaseSchema } from "@/types";

export interface Dish {
	name: string;
}

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
	materials: FileLinkSchema[];
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
	title: string;
	image: string;
	description: string;
	modifiers?: DishModifierSchema[];
	materials?: DishMaterials;
}

//
