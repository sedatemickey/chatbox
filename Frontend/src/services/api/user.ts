import axios, { AxiosError, type AxiosResponse, type AxiosInstance } from 'axios'
import API from '@/services/api/api'

interface ErrorResponse {
    detail: string
}

class userAPI {
    private static instance: userAPI
    private constructor() {}
    public static getInstance(): userAPI {
        if (!userAPI.instance) {
            userAPI.instance = new userAPI()
        }
        return userAPI.instance
    }

    public async addFriend(friendName: string): Promise<AxiosResponse<any>> {
        try {
            const data = {
                "username": friendName
            }
            const response = await API.getapi().post('/user/friends/add', data)
            return response
        }
        catch (error) {
            const { response } = error as AxiosError<ErrorResponse>
            throw response
        }
    }

    public async removeFriend(friend_id: string): Promise<AxiosResponse<any>> {
        try {
            const data = {
                user_id: friend_id
            }
            const response = await API.getapi().delete('/user/friends/delete', { data })
            return response
        }
        catch (error) {
            const { response } = error as AxiosError<ErrorResponse>
            throw response
        }
    }

    public async createGroup(groupname: string): Promise<AxiosResponse<any>> {
        try {
            const data = {
                "groupname": groupname
            }
            const response = await API.getapi().post('/user/groups/create', data)
            return response
        }
        catch (error) {
            const { response } = error as AxiosError<ErrorResponse>
            throw response
        }
    }

    public async joinGroup(id: string): Promise<AxiosResponse<any>> {
        try {
            const data = {
                "group_id": id
            }
            const response = await API.getapi().post('/user/groups/join', data)
            return response
        }
        catch (error) {
            const { response } = error as AxiosError<ErrorResponse>
            throw response
        }
    }

    public async removeGroup(id: string): Promise<AxiosResponse<any>> {
        try {
            const data = {
                "group_id": id
            }
            const response = await API.getapi().delete('/user/groups/delete', { data })
            return response
        }
        catch (error) {
            const { response } = error as AxiosError<ErrorResponse>
            throw response
        }
    }

}

export default userAPI.getInstance()