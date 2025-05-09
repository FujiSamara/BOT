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
	canEdit?: boolean;
}

export interface KnowledgeRootDivision extends KnowledgeDivision {
	iconURL: string;
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

export interface IngredientSchema extends BaseSchema {
	id: number;
	title: string;
	amount: number;
}
export interface DishModifierSchema extends BaseSchema {
	title: string | undefined;
	ingredients: IngredientSchema[];
}
export interface DishModifierGroupSchema extends BaseSchema {
	title: string | undefined;
	modifiers: DishModifierSchema[];
}

export interface FileLinkSchema extends BaseSchema {
	url: string;
	name: string;
	size: number;
	created: string;
}

export function getExt(fileLink: FileLinkSchema): string {
	const names = fileLink.name.split(".");
	const ext = names[names.length - 1];
	return ext;
}

export interface DishMaterials {
	video?: FileLinkSchema;
	materials: FileLinkSchema[];
}

export interface DishCard extends Card {
	title: string;
	image: string;
	description: string;
	modifiers?: DishModifierGroupSchema[];
	materials?: DishMaterials;
}

//
