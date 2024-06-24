import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
    state() {
        return {

        }
    },
    actions: {
        async auth(): Promise<boolean> {
            // TODO: Make auth
            return true
        },
        async login(login: string, password: string): Promise<boolean> {
            // TODO: Make login
            return true
        }
    }
})