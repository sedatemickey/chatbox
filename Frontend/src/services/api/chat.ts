import axios, { AxiosError, type AxiosResponse, type AxiosInstance } from 'axios'
import API from '@/services/api/api'

interface ErrorResponse {
    detail: string
}

class ChatService {
    private static instance: ChatService
    private constructor() {}
    public static getInstance(): ChatService {
        if (!ChatService.instance) {
            ChatService.instance = new ChatService()
        }
        return ChatService.instance
    }

    public async getGroupList(): Promise<AxiosResponse<any>> {
        try {
            const response = await API.getapi().get('/user/groups/list')
            return response
        }
        catch (error) {
            const { response } = error as AxiosError<ErrorResponse>
            throw error
        }
    }

    public async getFriendList(): Promise<AxiosResponse<any>> {
        try {
            const response = await API.getapi().get('/user/friends/list')
            return response
        }
        catch (error) {
            const response  = error as AxiosError<ErrorResponse>
            throw response
        }
    }

    public async getAllUsers(): Promise<AxiosResponse<any>> {
        try {
            const response = await API.getapi().get('/user/fulllist')
            return response
        }
        catch (error) {
            const { response } = error as AxiosError<ErrorResponse>
            throw error
        }
    }

    public async getAllGroups(): Promise<AxiosResponse<any>> {
        try {
            const response = await API.getapi().get('/user/groups/fulllist')
            return response
        }
        catch (error) {
            const { response } = error as AxiosError<ErrorResponse>
            throw error
        }
    }

    private getAuthHeader() {
        const instance = API.getapi()
        const headers = instance.defaults.headers.common["Authorization"]
        return headers ? headers.toString() : '';
    }

    public async getAichatStream(message: string): Promise<ReadableStream<Uint8Array>> {
        try {
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), 30000) // 30秒超时
            
            const response = await fetch(import.meta.env.VITE_API_URL + '/aichat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream',
                    'Authorization': this.getAuthHeader()
                },
                body: JSON.stringify({ message }),
                signal: controller.signal
            })
            
            clearTimeout(timeoutId)
            
            if (!response.ok || !response.body) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }
            
            return response.body 
        } catch (error) {
            throw error
        }
        // try {
        //     const data = {"message": message}
        //     const response = await API.getapi().post('/aichat', data, {
        //         headers: {
        //             'Accept': 'text/event-stream',
        //             'X-Requested-With': 'XMLHttpRequest'
        //         },
        //         responseType: 'text', 
        //         onDownloadProgress: (progressEvent) => {
        //             const chunk = progressEvent.event.target.responseText;
        //             handleStreamChunk(chunk);
        //         },
        //         timeout: 180000,
        //     })
        //     return response
        // }
        // catch (error) {
        //     const { response } = error as AxiosError<ErrorResponse>
        //     throw error
        // }
    }

}

export default ChatService.getInstance()