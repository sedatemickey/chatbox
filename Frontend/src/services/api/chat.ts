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

}

export default ChatService.getInstance()