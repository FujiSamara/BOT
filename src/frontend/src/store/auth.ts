import { defineStore } from 'pinia'
import axios from 'axios'
import { Access } from '@/types'

export const useAuthStore = defineStore('auth', {
    state() {
        return {
            accesses: new Array<Access>()
        }
    },
    actions: {
        async auth(): Promise<boolean> {
            // TODO: Make auth
            this.accesses = await this.getUserAccesses()
            return true
        },
        async login(login: string, password: string): Promise<boolean> {
            // TODO: Make login
            this.accesses = await this.getUserAccesses()
            return true
        },
        async getUserAccesses(): Promise<Array<Access>> {
            // TODO: Make getting accesses.
            return [Access.Bid]
        }
    }
})
