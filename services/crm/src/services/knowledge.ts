import axios from "axios";
import { useNetworkStore } from "@/store/network";
import {
	Card,
	CardType,
	DishMaterials,
	DishModifierSchema,
	DivisionType,
	FileLinkSchema,
	KnowledgeDivision,
	KnowledgeSubdivision,
} from "@/components/knowledge/types";
import {
	actualToRouterPath,
	DIVISION_CHUNK_SIZE,
	routerToActualPath,
} from "@/components/knowledge";
import { DocumentSchema } from "@/types";

export class KnowledgeService {
	private _networkStore = useNetworkStore();

	constructor(private _endpoint: string) {}

	// Division
	public async getDivision(
		path: string,
		subdivisionsOffset: number,
	): Promise<KnowledgeDivision | undefined> {
		path = routerToActualPath(path);
		const url = `${this._endpoint}/divisions/?path=${path}&limit=${DIVISION_CHUNK_SIZE}&offset=${subdivisionsOffset}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));

		if (!resp.data) return;
		const row = resp.data;

		const division: KnowledgeDivision = {
			id: row.id,
			name: row.name,
			type: row.type,
			path: actualToRouterPath(row.path),
			subdivisionsCount: row.subdivisions.length,
			filesCount: 0,
			subdivisions: [],
		};

		for (const sub of row.subdivisions) {
			division.subdivisions.push({
				id: sub.id,
				name: sub.name,
				path: actualToRouterPath(sub.path),
				type: sub.type,
				filesCount: 0,
				subdivisionsCount: sub.subdivisions_count,
			});
		}

		return division;
	}

	public async findDivisions(
		term: string,
		subdivisionsOffset: number,
	): Promise<KnowledgeSubdivision[]> {
		const url = `${this._endpoint}/divisions/find/by/name?term=${term}&limit=${DIVISION_CHUNK_SIZE}&offset=${subdivisionsOffset}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		const rows = resp.data;
		const divisions: KnowledgeSubdivision[] = [];

		for (const row of rows) {
			divisions.push({
				id: row.id,
				name: row.name,
				path: actualToRouterPath(row.path),
				type: row.type,
				filesCount: row.files_count,
				subdivisionsCount: row.subdivisions_count,
			});
		}

		return divisions;
	}

	// Card
	public async getCard(
		id: number,
		type: DivisionType,
	): Promise<Card | undefined> {
		let url = `${this._endpoint}/dishes/${id}`;

		if (type == DivisionType.business) {
			url = url.replace("dishes", "cards");
		}
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		if (!resp.data) return;

		const row = resp.data;
		return row;
	}

	public async getDishModifiers(
		dish_id: number,
	): Promise<DishModifierSchema[] | undefined> {
		const url = `${this._endpoint}/dishes/${dish_id}/modifiers`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		if (!resp.data) return;

		return resp.data;
	}

	public async getDishMaterials(
		dish_id: number,
	): Promise<DishMaterials | undefined> {
		const url = `${this._endpoint}/dishes/${dish_id}/materials`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		if (!resp.data) return;

		if (resp.data.video === null) resp.data.video = undefined;

		return resp.data;
	}

	public async getBusinessMaterials(
		card_id: number,
	): Promise<FileLinkSchema[] | undefined> {
		const url = `${this._endpoint}/cards/${card_id}/materials`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		if (!resp.data) return;

		return resp.data;
	}

	public async updateCard(id: number, card_update: any, type: CardType) {
		switch (type) {
			case CardType.dish:
				await this.updateDishCard(id, card_update);
				break;
			case CardType.business:
				await this.updateBusinessCard(id, card_update);
				break;
		}
	}

	private async updateDishCard(id: number, card_update: any) {}

	private async updateBusinessCard(id: number, card_update: any) {
		const description: string = card_update["description"];
		const materials: DocumentSchema[] = card_update["materials"];

		let url = `${this._endpoint}/cards/${id}`;
		await this._networkStore.withAuthChecking(
			axios.patch(url, {
				description: description,
			}),
		);

		if (materials.length) {
			const meta_list = [];
			for (const material of materials) {
				meta_list.push({
					filename: material.name,
					size: material.file!.size,
				});
			}

			url = `${this._endpoint}/cards/${id}/materials`;
			const resp = await this._networkStore.withAuthChecking(
				axios.post(url, meta_list),
			);
			if (resp === undefined) return;
			const links: FileLinkSchema[] = resp.data;

			for (let index = 0; index < materials.length; index++) {
				const material = materials[index];
				const link = links[index];
				await axios.put(link.url, material.file, {
					headers: {
						"Content-Type": material.file!.type,
						Authorization: undefined,
					},
					withCredentials: false,
				});
			}
		}
	}
}
