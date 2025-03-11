import API from "@/services/api/api"
import { showMessage } from "@/utils/message"
import { ref, type Ref } from "vue"

class WebSocketService {
    private static instance: WebSocketService
    private ws: WebSocket
    wsMessage: Ref<string> = ref("")

    private constructor() {
        this.ws = new WebSocket(import.meta.env.VITE_API_URL + "/ws")
        this.ws.onopen = () => {
            console.warn('WebSocket connected')
            this.authorizeWebSocket(API.getToken())
        }
        this.ws.onmessage = (event) => {
            console.warn('WebSocket message received: ', event.data)
            showMessage.success(event.data)
            if (event.data.startsWith("getMessage: ")) {
                this.wsMessage.value = event.data.slice(11)
            }
        }
        this.ws.onerror = (event) => {
            console.error('WebSocket error: ', event)
            showMessage.error("WebSocket连接异常")
        }
        this.ws.onclose = (event) => {
            console.warn('WebSocket closed: ', event)
            showMessage.error("WebSocket连接断开")
        }
    }
    public static getInstance(): WebSocketService {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService()
        }
        return WebSocketService.instance
    }
    private authorizeWebSocket(token: string | null) {
        this.sendJSON({
            type: "auth_request",
            token: token
        })
    }

    public sendText(message: string) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message)
        } else {
            console.error("WebSocket is not open")
            showMessage.error("WebSocket连接异常")
        }
    }

    public sendJSON <T extends object>(data: T): void {
        console.warn('Sending JSON data: ', data)
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error("WebSocket is not open")
            showMessage.error("WebSocket连接异常")
        }
    }

}

export default WebSocketService.getInstance()