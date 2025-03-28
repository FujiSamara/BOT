import axios from "axios";
import { useNetworkStore } from "@/store/network";
import {
	KnowledgeDivision,
	KnowledgeSubdivision,
} from "@/components/knowledge";
export class KnowledgeService {
	private _networkStore = useNetworkStore();

	private _routerToActual = {
		product: "Продукт",
		marketing: "Маркетинг",
		purchases: "Закупки",
	};

	constructor(private _endpoint: string) {}

	private routerToActualPath(path: string): string {
		let result = path;
		for (const key of Object.keys(this._routerToActual)) {
			result = result.replace(key, (this._routerToActual as any)[key]);
		}
		return result;
	}

	private actualToRouterPath(path: string): string {
		let result = path;
		for (const key of Object.keys(this._routerToActual)) {
			result = result.replace((this._routerToActual as any)[key], key);
		}
		return result;
	}

	public async getDivision(
		path: string,
	): Promise<KnowledgeDivision | undefined> {
		path = this.routerToActualPath(path);
		const url = `${this._endpoint}/division/?path=${path}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));

		if (!resp.data) return;
		const row = resp.data;

		const division: KnowledgeDivision = {
			id: row.id,
			name: row.name,
			type: row.type,
			path: this.actualToRouterPath(row.path),
			subdivisionsCount: row.subdivisions.length,
			filesCount: 0,
			subdivisions: [],
		};

		for (const sub of row.subdivisions) {
			division.subdivisions.push({
				id: sub.id,
				name: sub.name,
				path: this.actualToRouterPath(sub.path),
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
				path: this.actualToRouterPath(row.path),
				type: row.type,
				filesCount: row.files_count,
				subdivisionsCount: row.subdivisions_count,
			});
		}

		return divisions;
	}
}
