import axios from "axios";

import * as config from "@/config";
import { useNetworkStore } from "@/store/network";
import { BaseSchema, QuerySchema, InfoSchema, BidSchema } from "@/types";

export class PathOptions {
	getExtraPath: string = "";
	getInfoExtraPath: string = "";
	createExtraPath: string = "";
	updateExtraPath: string = "";
	deleteExtraPath: string = "";
	exportExtraPath: string = "";
}

/** Service for handle requests to entity */
export default class EntityService<T extends BaseSchema> {
	protected _networkStore = useNetworkStore();
	protected _endpoint = `${config.coreURL}/${config.crmEndpoint}`;

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

		const url = `${this._endpoint}/${name}${this.options.getInfoExtraPath}/page/info?records_per_page=${rowsPerPage}`;
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

		const url = `${this._endpoint}/${name}${this.options.getExtraPath}/page/${page}?records_per_page=${rowsPerPage}`;
		const resp = await this._networkStore.withAuthChecking(
			axios.post(url, query),
		);
		return resp.data;
	}

	public async createEntity(entity: T, name: string = this.entityName) {
		await this._networkStore.withAuthChecking(
			axios.post(
				`${this._endpoint}/${name}${this.options.createExtraPath}/`,
				entity,
			),
		);
	}

	public async updateEntity(entity: T, name: string = this.entityName) {
		await this._networkStore.withAuthChecking(
			axios.patch(
				`${this._endpoint}/${name}${this.options.updateExtraPath}/`,
				entity,
			),
		);
	}

	public async deleteEntity(id: number, name: string = this.entityName) {
		await this._networkStore.withAuthChecking(
			axios.delete(
				`${this._endpoint}/${name}${this.options.deleteExtraPath}/${id}`,
			),
		);
	}

	public async exportEntities(
		query?: QuerySchema,
		name: string = this.entityName,
	) {
		const resp = await this._networkStore.withAuthChecking(
			axios.post(
				`${this._endpoint}/${name}${this.options.exportExtraPath}/export`,
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

	public async searchEntities(
		term: string,
		name: string = this.entityName,
	): Promise<T[]> {
		const url = `${this._endpoint}/${name}/by/name?name=${term}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		return resp.data;
	}

	public async getEntityByID(id: number): Promise<T | undefined> {
		const url = `${this._endpoint}/${this.entityName}/${id}`;
		const resp = await this._networkStore.withAuthChecking(axios.get(url));
		return resp.data;
	}
}

export class BidPathOptions extends PathOptions {
	approveExtraPath: string = "";
	rejectExtraPath: string = "";
}

export class BidService extends EntityService<BidSchema> {
	constructor(
		public entityName: string,
		public options: BidPathOptions = new BidPathOptions(),
	) {
		super(entityName, options);
	}

	public async createEntity(
		entity: BidSchema,
		name: string = this.entityName,
	): Promise<void> {
		const data = new FormData();
		entity.documents.map((doc) => data.append("files", doc.file!, doc.name));

		const resp = await this._networkStore.withAuthChecking(
			axios.post(
				`${this._endpoint}/${name}${this.options.createExtraPath}/`,
				entity,
			),
		);

		await this._networkStore.withAuthChecking(
			axios.post(
				`${this._endpoint}/${name}${this.options.createExtraPath}/${resp.data.id}`,
				data,
				{
					headers: {
						"Content-Type": `multipart/form-data`,
					},
				},
			),
		);
	}

	public async approveBid(id: number, name: string = this.entityName) {
		await this._networkStore.withAuthChecking(
			axios.patch(
				`${this._endpoint}/${name}${this.options.approveExtraPath}/approve/${id}`,
			),
		);
	}

	public async rejectBid(
		id: number,
		reason: string,
		name: string = this.entityName,
	) {
		await this._networkStore.withAuthChecking(
			axios.patch(
				`${this._endpoint}/${name}${this.options.rejectExtraPath}/reject/${id}?reason=${reason}`,
			),
		);
	}
}
