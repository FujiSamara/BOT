import { defineStore } from "pinia";
import { Access, accessesDict, Token } from "@/types";
import axios, { AxiosResponse } from "axios";
import * as config from "@/config";
import { inject } from "vue";
import { VueCookies } from "vue-cookies";
import { jwtDecode } from "jwt-decode";
import router from "@/router";
import FileSaver from "file-saver";

export const useNetworkStore = defineStore("network", {
	state() {
		const $cookies = inject<VueCookies>("$cookies")!;
		const access_token = $cookies.get("access_token");
		const token_type = $cookies.get("token_type");

		if (access_token && token_type) {
			axios.defaults.headers.common["Authorization"] =
				`${token_type} ${access_token}`;
		}

		// Global axios settings
		axios.defaults.withCredentials = true;

		return {
			accesses: new Array<Access>(),
			$cookies: $cookies,
			username: undefined,
		};
	},
	actions: {
		async auth(): Promise<boolean> {
			const url = `${config.fullBackendURL}/${config.authEndpoint}/`;

			return await axios
				.get(url)
				.then(() => {
					const access_token = this.$cookies.get("access_token");
					this.setUserData(access_token);

					return true;
				})
				.catch(() => false);
		},
		async login(username: string, password: string): Promise<boolean> {
			const url = `${config.fullBackendURL}/${config.authEndpoint}/token`;

			return await axios
				.post(
					url,
					{
						username: username,
						password: password,
						scope: "admin",
					},
					{
						headers: {
							"Content-Type": "multipart/form-data",
						},
					},
				)
				.then((resp) => {
					const data: Token = resp.data;
					axios.defaults.headers.common["Authorization"] =
						`${data.token_type} ${data.access_token}`;
					this.$cookies.set("access_token", data.access_token);
					this.$cookies.set("token_type", data.token_type);

					return true;
				})
				.catch(() => {
					return false;
				});
		},
		setUserData(token: string): void {
			const decoded: any = jwtDecode(token);
			this.accesses = [];
			for (const scope of decoded.scopes) {
				if (accessesDict[scope] !== undefined)
					this.accesses.push(accessesDict[scope]);
			}
			this.username = decoded.sub;
		},
		logout(): void {
			this.$cookies.remove("access_token");
			this.$cookies.remove("token_type");
			axios.defaults.headers.common["Authorization"] = undefined;
			router.push({ name: "login" });
		},
		async withAuthChecking(
			handler: Promise<AxiosResponse<any, any>>,
		): Promise<any> {
			return await handler.catch((error) => {
				const statusCode = error.response ? error.response.status : null;

				if (statusCode === 401) {
					router.go(0);
				} else {
					return Promise.reject(error);
				}
			});
		},
		async getFile(href: string): Promise<Uint8Array> {
			const resp = await this.withAuthChecking(
				axios.get(href, {
					responseType: "blob",
				}),
			);

			return resp.data as Uint8Array;
		},
		async downloadFile(href: string, filename: string) {
			this.saveFile(filename, await this.getFile(href));
		},
		saveFile(filename: string, file: Uint8Array) {
			const fileBlob = new Blob([file], {
				type: "application/octet-stream",
			});

			FileSaver.saveAs(fileBlob, filename);
		},
	},
});
