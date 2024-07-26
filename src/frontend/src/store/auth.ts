import { defineStore } from "pinia";
import { Access, accessesDict, Token } from "@/types";
import axios from "axios";
import * as config from "@/config";
import { inject } from "vue";
import { VueCookies } from "vue-cookies";
import { jwtDecode } from "jwt-decode";
import router from "@/router";

export const useAuthStore = defineStore("auth", {
	state() {
		const $cookies = inject<VueCookies>("$cookies")!;
		const access_token = $cookies.get("access_token");
		const token_type = $cookies.get("token_type");

		if (access_token && token_type) {
			axios.defaults.headers.common["Authorization"] =
				`${token_type} ${access_token}`;
		}

		axios.defaults.withCredentials = true;

		return {
			accesses: new Array<Access>(),
			$cookies: $cookies,
		};
	},
	actions: {
		async auth(): Promise<boolean> {
			const url = `${config.fullBackendURL}/${config.authEndpoint}/`;

			return await axios
				.get(url)
				.then(() => {
					const access_token = this.$cookies.get("access_token");
					this.setUserAccesses(access_token);

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
		setUserAccesses(token: string): void {
			const decoded: any = jwtDecode(token);

			this.accesses = [];
			for (const scope of decoded.scopes) {
				if (accessesDict[scope]) this.accesses.push(accessesDict[scope]);
			}
		},
		logout(): void {
			this.$cookies.remove("access_token");
			this.$cookies.remove("token_type");
			axios.defaults.headers.common["Authorization"] = undefined;
			router.push({ name: "login" });
		},
	},
});
