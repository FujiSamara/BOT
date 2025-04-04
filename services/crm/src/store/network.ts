import { defineStore } from "pinia";
import { Access, accessesDict, Token } from "@types";
import axios, { AxiosError, AxiosResponse } from "axios";
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
			errors: new Array<string>(),
			authing: false,
			authorized: false,
		};
	},
	actions: {
		async auth(): Promise<boolean> {
			const url = `${config.coreURL}/${config.authEndpoint}/`;
			this.authing = true;

			return await axios
				.get(url)
				.then((resp) => {
					this.setUserData(resp.data.access_token);
					this.authing = false;
					this.authorized = true;

					return true;
				})
				.catch(() => {
					this.authing = false;
					return false;
				});
		},
		async login(username: string, password: string): Promise<boolean> {
			const url = `${config.coreURL}/${config.authEndpoint}/token`;

			return await axios
				.post(
					url,
					{
						username: username,
						password: password,
					},
					{
						headers: {
							"Content-Type": "multipart/form-data",
						},
					},
				)
				.then((resp) => {
					const data: Token = resp.data;
					this.setCredentials(data.access_token, data.token_type);
					this.setUserData(data.access_token);

					this.authorized = true;

					return true;
				})
				.catch(() => {
					return false;
				});
		},
		setCredentials(token: string, token_type: string): void {
			token_type =
				token_type[0].toUpperCase() + token_type.substring(1).toLowerCase();
			axios.defaults.headers.common["Authorization"] = `${token_type} ${token}`;
			this.$cookies.set("access_token", token);
			this.$cookies.set("token_type", token_type);
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
			this.authorized = false;
		},
		async withAuthChecking(
			handler: Promise<AxiosResponse<any, any>>,
		): Promise<any> {
			return await handler.catch(async (error: AxiosError) => {
				const statusCode = error.response ? error.response.status : null;

				let msg;

				if (statusCode === 401) {
					if (!(await this.auth())) {
						router.go(0);
					}

					msg =
						"У вас нет доступа к этой панели. " +
						"Вы можете попробовать обновить страницу, " +
						"либо обратиться к администратору. \n" +
						"URL: " +
						error.config?.url;
				} else {
					if (error.response && (error.response.data as any).detail) {
						msg = JSON.stringify((error.response.data as any).detail);
					} else {
						msg = error.message;
					}

					alert("Произошла ошибка:\n" + msg);
				}

				this.errors.push(msg);
				return Promise.reject(error);
			});
		},
		async getFile(filename: string): Promise<Uint8Array> {
			return this.getFileByURL(
				`${config.coreURL}/${config.filesEndpoint}?name=${filename}`,
			);
		},
		async getFileByURL(href: string): Promise<Uint8Array> {
			const resp = await this.withAuthChecking(
				axios.get(href, {
					responseType: "blob",
				}),
			);

			return resp.data as Uint8Array;
		},
		async downloadFile(filename: string, href?: string) {
			if (href) {
				this.saveFile(filename, await this.getFileByURL(href));
			} else {
				this.saveFile(filename, await this.getFile(filename));
			}
		},
		saveFile(filename: string, file: Uint8Array) {
			const fileBlob = new Blob([file], {
				type: "application/octet-stream",
			});

			FileSaver.saveAs(fileBlob, filename);
		},
		async putToS3(urls: string[], files: Blob[]) {
			for (let index = 0; index < urls.length; index++) {
				const file = files[index];
				const url = urls[index];
				try {
					await axios.put(url, file, {
						headers: {
							"Content-Type": file.type,
							Authorization: undefined,
						},
						withCredentials: false,
					});
				} catch {}
			}
		},
	},
});
