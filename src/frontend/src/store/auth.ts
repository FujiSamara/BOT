import { defineStore } from "pinia";
import { Access } from "@/types";

export const useAuthStore = defineStore("auth", {
	state() {
		return {
			accesses: new Array<Access>(),
		};
	},
	actions: {
		async auth(): Promise<boolean> {
			// TODO: Make auth
			this.accesses = await this.getUserAccesses();
			return false;
		},
		async login(_1: string, _2: string): Promise<boolean> {
			// TODO: Make login
			this.accesses = await this.getUserAccesses();
			return true;
		},
		async getUserAccesses(): Promise<Array<Access>> {
			// TODO: Make getting accesses.
			return [Access.Bid, Access.Expenditure];
		},
		async logout(): Promise<void> {
			return;
		},
	},
});
