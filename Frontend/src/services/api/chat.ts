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

}

export default ChatService.getInstance()