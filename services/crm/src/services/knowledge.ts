import axios from "axios";
import { useNetworkStore } from "@/store/network";
import {
	KnowledgeDivision,
	KnowledgeSubdivision,
	routerToActualPath,
	actualToRouterPath,
	DivisionType,
	Card,
	DIVISION_CHUNK_SIZE,
} from "@/components/knowledge";

export class KnowledgeService {
	private _networkStore = useNetworkStore();

	constructor(private _endpoint: string) {}

	public async getDivision(
		path: string,
		subdivisionsOffset: number,
	): Promise<KnowledgeDivision | undefined> {
		path = routerToActualPath(path);
		const url = `${this._endpoint}/division/?path=${path}&limit=${DIVISION_CHUNK_SIZE}&offset=${subdivisionsOffset}`;
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
		const url = `${this._endpoint}/division/find/by/name?term=${term}&limit=${DIVISION_CHUNK_SIZE}&offset=${subdivisionsOffset}`;
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

	public async getCard(
		id: number,
		type: DivisionType,
	): Promise<Card | undefined> {
		let url = `${this._endpoint}/dish/${id}`;

		if (type == DivisionType.business) {
			url = url.replace("dish", "card");
		}
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		if (!resp.data) return;

		const row = resp.data;
		row.name = row.title;
		return row;
	}
}
