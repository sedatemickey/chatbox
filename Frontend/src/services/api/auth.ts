import { AxiosError } from 'axios'
import { message } from '@/utils/message'
import API from '@/services/api/api'

interface LoginResponse {
    access_token: string
    token_type: string
    expires: number
}

interface ErrorResponse {
    detail: string
}


class TokenManager {
    private static instance: TokenManager
    private refreshTimeout: number | null = null

    private constructor() {
        this.initializeToken()
    }

    public static getInstance(): TokenManager {
        if (!TokenManager.instance) {
            TokenManager.instance = new TokenManager()
        }
        return TokenManager.instance
    }

    private initializeToken() {
        const token = localStorage.getItem('access_token')
        const tokenType = localStorage.getItem('token_type')
        const expiresAt = localStorage.getItem('expires_at')

        if (token && tokenType && expiresAt) {
            API.setAuthorization(tokenType, token)
            this.scheduleRefresh(parseInt(expiresAt))
        }
    }

    public setToken(response: LoginResponse): void {
        const { access_token, token_type, expires } = response
        const expiresAt = Date.now() + expires * 60 * 1000

        localStorage.setItem('access_token', access_token)
        localStorage.setItem('token_type', token_type)
        localStorage.setItem('expires_at', expiresAt.toString())

        API.setAuthorization(token_type, access_token)
        this.scheduleRefresh(expiresAt)
    }

    private scheduleRefresh(expiresAt: number): void {
        const refreshTime = expiresAt - 5 * 60 * 1000

        if (this.refreshTimeout) {
            clearTimeout(this.refreshTimeout)
        }

        this.refreshTimeout = window.setTimeout(() => {
            this.refreshToken()
        }, refreshTime - Date.now())
    }

    public async refreshToken(): Promise<void> {
        try {
            const response = await API.getapi().post<LoginResponse>('/auth/refresh_token')
            this.setToken(response.data)
        } catch (error) {
            const axiosError = error as AxiosError<ErrorResponse>
            if (axiosError.response?.status === 401) {
                console.log('Refresh token failed:', axiosError.response.data.detail)
                this.clearToken()
            }
        }
    }

    public clearToken(): void {
        localStorage.removeItem('access_token')
        localStorage.removeItem('token_type')
        localStorage.removeItem('expires_at')
        API.removeAuthorization()
        if (this.refreshTimeout) {
            clearTimeout(this.refreshTimeout)
        }
    }
}

export const tokenManager = TokenManager.getInstance()

export const handleLogin = async (username: string, password: string): Promise<void> => {
    try {
        const response = await API.getapi().post<LoginResponse>('/auth/login', {
            username,
            password
        })
        tokenManager.setToken(response.data)
        message.success('Login successful')
        window.location.href = '/chat'
    } catch (error) {
        const axiosError = error as AxiosError<ErrorResponse>
        if (axiosError.response?.status === 401) {
            console.log('Login failed:', axiosError.response.data.detail)
            message.error(axiosError.response.data.detail)
        }
        throw error
    }
}

export const handleRegister = async (username: string, password: string): Promise<void> => {
    try {
        const response = await API.getapi().post<LoginResponse>('/auth/register', {
            username,
            password
        })
        tokenManager.setToken(response.data)
        message.success('Registration successful')
        window.location.href = '/chat'
    } catch (error) {
        const axiosError = error as AxiosError<ErrorResponse>
        if (axiosError.response?.status === 422) {
            console.log('Registration failed:', axiosError.response.data.detail)
            message.error(axiosError.response.data.detail)
        }
        throw error
    }
}

export const checkToken = async (): Promise<boolean> => {
    const expiresAt = localStorage.getItem('expires_at')
    const timeNow = Date.now()
    if (expiresAt && parseInt(expiresAt) > timeNow) {
        return true
    }
    else {
        tokenManager.clearToken()
        return false
    }
}