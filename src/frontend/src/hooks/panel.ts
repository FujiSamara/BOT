import { Table } from "@/types";
import { computed, ComputedRef } from "vue";
import axios from "axios";
import * as config from "@/config";

async function loadData(endpoint: string) {
	console.log(endpoint);
	return await axios.get(`${endpoint}s`);
}

export default function usePanelDataHandler(
	table: Table,
	panelName: string,
): ComputedRef<void> {
	const endpoint = `http://${config.backendDomain}:${config.backendPort}/${config.crmEndpoint}/panel/${panelName}`;
	const panelData = loadData(endpoint);
	return computed(() => {
		const data = panelData;
		console.log(data);
	});
}
