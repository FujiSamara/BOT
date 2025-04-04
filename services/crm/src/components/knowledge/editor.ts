import {
	BaseEntity,
	DocumentEntity,
	SelectType,
	StringInputEntity,
} from "@/components/entity";
import {
	BusinessCard,
	Card,
	CardType,
	DishCard,
} from "@/components/knowledge/types";

export interface Field {
	entity: BaseEntity<any>;
	type: SelectType;
}

function getBusinessCardFields(card: BusinessCard): Field[] {
	const description = new StringInputEntity(false, "Описание");
	if (card.description !== undefined) description.init(card.description);

	return [
		{
			entity: description,
			type: SelectType.Input,
		},
		{
			entity: new DocumentEntity(false, "Материалы"),
			type: SelectType.MultiDocument,
		},
	];
}

function getDishCardFields(dish: DishCard): Field[] {
	const result = [];

	if (dish.materials === undefined || dish.materials.video === undefined) {
		result.push({
			entity: new DocumentEntity(false, "Видео"),
			type: SelectType.MonoDocument,
		});
	}

	result.push({
		entity: new DocumentEntity(false, "Материалы"),
		type: SelectType.MultiDocument,
	});

	return result;
}

function toBusinessCardUpdate(fields: Field[]) {
	const description = fields[0].entity;
	const materials = fields[1].entity;

	return {
		description: description.getResult(),
		materials: materials.getResult(),
	};
}

function toDishCardUpdate(fields: Field[]) {
	const result: any = {};

	if (fields.length === 2) {
		result["video"] = fields[0].entity.getResult();
		result["materials"] = fields[1].entity.getResult();
	} else {
		result["materials"] = fields[0].entity.getResult();
	}

	return result;
}

export function getCardFields(card: Card): Field[] {
	switch (card.type) {
		case CardType.business:
			return getBusinessCardFields(card as BusinessCard);
		case CardType.dish:
			return getDishCardFields(card as DishCard);
	}
}

export function toCardUpdate(cardType: CardType, fields: Field[]) {
	switch (cardType) {
		case CardType.business:
			return toBusinessCardUpdate(fields);
		case CardType.dish:
			return toDishCardUpdate(fields);
	}
}
