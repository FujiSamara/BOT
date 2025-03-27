import axios from "axios";
import { useNetworkStore } from "@/store/network";
import { DivisionType, KnowledgeDivision } from "@/components/knowledge";
export class KnowledgeService {
	private _networkStore = useNetworkStore();

	constructor(private _endpoint: string) {}

	public async getDivision(
		path: string,
	): Promise<KnowledgeDivision | undefined> {
		const url = `${this._endpoint}/division/?path=${path}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));

		if (!resp.data) return;

		const division = resp.data as KnowledgeDivision;

		switch (division.type) {
			case DivisionType.division:
				division.childrenCount = division.subdivisions.length;
				break;
			case DivisionType.dish:
				division.childrenCount = 0;
				break;
			case DivisionType.business:
				division.childrenCount = 0;
				break;
		}

		division.filesCount = 0;
		return division;
	}
}
