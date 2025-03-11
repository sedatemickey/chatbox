import axios, { AxiosError, type AxiosResponse, type AxiosInstance } from 'axios'

interface ErrorResponse {
    detail: string
}

class API {
    private static instance: API
    private readonly api = axios.create({
        baseURL: import.meta.env.VITE_API_URL,
        timeout: 5000,
        headers: {
            'Content-Type': 'application/json'
        }
    })
    private token: string | null = null

    private constructor() {
        this.api.interceptors.response.use(
            (response: AxiosResponse) => response,
            async (error: AxiosError<ErrorResponse>) => {
                if (error.response?.status === 401) {
                    console.log('API 401 Authentication error:', error.response.data.detail)
                }
                if (error.response?.status === 422) {
                    console.log('API 422 Validation error:', error.response.data.detail)
                }
                return Promise.reject(error)
            }
        )
    }

    public static getInstance(): API {
        if (!API.instance) {
            API.instance = new API()
        }
        return API.instance
    }

    public setAuthorization(tokenType: string, token: string): void {
        this.api.defaults.headers.common['Authorization'] = `${tokenType} ${token}`
        this.token = token
        console.log('Authorization set:', tokenType, token)
    }

    public removeAuthorization(): void {
        delete this.api.defaults.headers.common['Authorization']
        this.token = null
        console.log('Authorization removed')
    }

    public getapi(): AxiosInstance {
        return this.api
    }

    public getToken(): string | null {
        return this.token
    }

}

export default API.getInstance()