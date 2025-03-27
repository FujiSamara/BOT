import axios from "axios";
import { useNetworkStore } from "@/store/network";
import {
	KnowledgeDivision,
	KnowledgeSubdivision,
} from "@/components/knowledge";
export class KnowledgeService {
	private _networkStore = useNetworkStore();

	constructor(private _endpoint: string) {}

	public async getDivision(
		path: string,
	): Promise<KnowledgeDivision | undefined> {
		const url = `${this._endpoint}/division/?path=${path}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));

		if (!resp.data) return;
		const row = resp.data;

		const division: KnowledgeDivision = {
			id: row.id,
			name: row.name,
			type: row.type,
			path: row.path,
			subdivisionsCount: row.subdivisions.length,
			filesCount: 0,
			subdivisions: [],
		};

		for (const sub of row.subdivisions) {
			division.subdivisions.push({
				id: sub.id,
				name: sub.name,
				path: sub.path,
				type: sub.type,
				filesCount: 0,
				subdivisionsCount: sub.subdivisions_count,
			});
		}

		return division;
	}

	public async findDivisions(term: string): Promise<KnowledgeSubdivision[]> {
		const url = `${this._endpoint}/division/find/by/name?term=${term}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		const rows = resp.data;
		const divisions: KnowledgeSubdivision[] = [];

		for (const row of rows) {
			divisions.push({
				id: row.id,
				name: row.name,
				path: row.path,
				type: row.type,
				filesCount: row.files_count,
				subdivisionsCount: row.subdivisions_count,
			});
		}

		return divisions;
	}
}
