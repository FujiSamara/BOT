import axios from "axios";

import * as config from "@/config";
import { useNetworkStore } from "@/store/network";
import { BaseSchema, QuerySchema, InfoSchema } from "@/types";

class PathOptions {
	getExtraPath: string = "";
	getInfoExtraPath: string = "";
	createExtraPath: string = "";
	updateExtraPath: string = "";
	deleteExtraPath: string = "";
	approveExtraPath: string = "";
	rejectExtraPath: string = "";
	exportExtraPath: string = "";
}

/** Service for handle requests to entity */
export default class EntityService<T extends BaseSchema> {
	private _networkStore = useNetworkStore();
	private _endpoint = `${config.coreURL}/${config.crmEndpoint}`;

	constructor(
		public entityName: string,
		public options: PathOptions = new PathOptions(),
	) {}

	public async getEntitiesInfo(
		query?: QuerySchema,
		rowsPerPage?: number,
		name: string = this.entityName,
	): Promise<InfoSchema> {
		rowsPerPage ||= 1e3;
		query ||= {};

		const url = `${this._endpoint}${this.options.getInfoExtraPath}/${name}/page/info?records_per_page=${rowsPerPage}`;
		const resp = await this._networkStore.withAuthChecking(
			axios.post(url, query),
		);
		return resp.data;
	}

	public async getEntities(
		query?: QuerySchema,
		page?: number,
		rowsPerPage?: number,
		name: string = this.entityName,
	): Promise<T[]> {
		page ||= 1;
		rowsPerPage ||= 1e3;
		query ||= {};

		const url = `${this._endpoint}${this.options.getExtraPath}/${name}/page/${page}?records_per_page=${rowsPerPage}`;
		const resp = await this._networkStore.withAuthChecking(
			axios.post(url, query),
		);
		return resp.data;
	}

	public async createEntity(entity: T) {
		await this._networkStore
			.withAuthChecking(
				axios.post(`${this._endpoint}${this.options.createExtraPath}/`, entity),
			)
			.catch((_) => {});
	}

	public async updateEntity(entity: T) {
		await this._networkStore
			.withAuthChecking(
				axios.patch(
					`${this._endpoint}${this.options.updateExtraPath}/`,
					entity,
				),
			)
			.catch((_) => {});
	}

	public async deleteEntity(id: number) {
		await this._networkStore
			.withAuthChecking(
				axios.delete(`${this._endpoint}${this.options.deleteExtraPath}/${id}`),
			)
			.catch((_) => {});
	}

	public async exportEntities(query?: QuerySchema) {
		const resp = await this._networkStore.withAuthChecking(
			axios.post(
				`${this._endpoint}${this.options.exportExtraPath}/export`,
				query,
				{
					responseType: "blob",
					withCredentials: true,
				},
			),
		);
		const filename = (resp.headers["content-disposition"] as string).split(
			"=",
		)[1];

		this._networkStore.saveFile(filename, resp.data);
	}

	public async searchEntities(term: string): Promise<T[]> {
		const url = `${this._endpoint}/${this.entityName}/by/name?name=${term}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		return resp.data;
	}

	public async getEntityByID(id: number): Promise<T | undefined> {
		const url = `${this._endpoint}/${this.entityName}/${id}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		return resp.data;
	}
}
