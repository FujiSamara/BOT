import axios from "axios";
import { useNetworkStore } from "@/store/network";
import { KnowledgeDivision } from "@/components/knowledge";
export class KnowledgeService {
	private _networkStore = useNetworkStore();

	constructor(private _endpoint: string) {}

	public async getDivision(path: string): Promise<KnowledgeDivision> {
		const url = `${this._endpoint}/division/?path=${path}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));

		console.log(resp);
	}
}
