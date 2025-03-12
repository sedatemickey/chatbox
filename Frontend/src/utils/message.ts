// src/utils/message.ts
import { createApp, type App, type Plugin } from 'vue'
import Message from '@/components/Message.vue'

// 创建消息实例
let messageInstance: any = null

const initMessage = () => {
    const mountNode = document.createElement('div')
    document.body.appendChild(mountNode)
    return createApp(Message).mount(mountNode)
}

export const showMessage = {
    success: (msg: string, duration?: number) => {
        if (!messageInstance) messageInstance = initMessage()
        messageInstance.show(msg, 'success', duration)
    },
    error: (msg: string, duration?: number) => {
        if (!messageInstance) messageInstance = initMessage()
        messageInstance.show(msg, 'error', duration)
    }
}

// 保留插件安装方式
export default {
    install(app: App) {
        app.config.globalProperties.$showMessage = showMessage
    }
} as Plugin