<template>
    <div class="chat-container">
        <div class="background-image"></div>
        <div class="logout-container">
            <el-tooltip 
                content="退出登录" 
                placement="left"
                effect="light"
            >
                <button 
                    class="logout-btn"
                    @click="handleLogout"
                >
                <i class="icon-signout"></i>
                </button>
            </el-tooltip>
        </div>
        <div class="main-content">

            <div class="left-sidebar">
                <div class="header">
                    <h2>聊天列表</h2>
                    <el-button 
                        class="circle-btn"
                        type="primary"
                        @click="showAddDialog = true"
                    >
                    <el-icon><Plus /></el-icon>
                    </el-button>
                </div>
                <ul class="contact-list">
                    <li v-for="item in chatList" 
                        :key="item.id" 
                        :class="{ active: selectedChat?.id === item.id }"
                        @click="selectChat(item)">
                        <div class="avatar">{{ item.name.charAt(0) }}</div>
                        <div class="info">
                            <h3>{{ item.name }}</h3>
                            <p>{{ item.lastMessage }}</p>
                        </div>
                    </li>
                </ul>
            </div>
    
            <div class="right-content">
                <div v-if="selectedChat" class="chat-area">
                    <div class="chat-header">
                        <div class="chat-avatar">{{ selectedChat.name.charAt(0) }}</div>
                        <h2>{{ selectedChat.name }}</h2>
                    </div>
                    
                    <div class="messages-container" ref="messagesContainer" @scroll.passive="handleScroll">
                        <div v-for="(message, index) in messages" 
                            :key="index"
                            :class="['message-bubble', message.sender === 'me' ? 'sent' : 'received']">
                            <div class="content">{{ message.content }}</div>
                            <div class="timestamp">{{ formatTime(message.timestamp) }}</div>
                        </div>
                    </div>
        
                    <div class="message-input">
                        <input v-model="newMessage" 
                                @keyup.enter="sendMessage"
                                placeholder="输入消息...">
                        <button @click="sendMessage">发送</button>
                    </div>
                </div>
        
                <div v-else class="empty-chat">
                    <div class="welcome-text">选择聊天对象开始对话</div>
                </div>
            </div>
        </div>
    
        <transition name="fade">
            <div v-if="showAddDialog" class="add-dialog">
                <div class="dialog-content">
                    <FriendGroupModal 
                        @close="showAddDialog = false"
                        :friends="friendList"
                        :groups="groupList"
                        :allUsers="allUsersList"
                        :allGroups="allGroupsList"
                        :getChatList="getChatList.bind(this)"
                    />
                </div>
            </div>
        </transition>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import ChatService from '@/services/api/chat'
import { showMessage } from '@/utils/message'
import { checkToken } from '@/services/api/auth'
import WebSocketService from '@/services/websocket'
import FriendGroupModal from '@/components/FriendGroupModal.vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { tokenManager } from '@/services/api/auth'
import { Plus } from '@element-plus/icons-vue'
import chat from '@/services/api/chat'

interface ChatItem {
    id: string
    name: string
    type: 'friend' | 'group'
    lastMessage: string
}

interface Message {
    content: string
    timestamp: number
    sender: 'me' | 'other'
}


const chatList = ref<ChatItem[]>([])
const selectedChat = ref<ChatItem | null>(null)
const messages = ref<Message[]>([])
const newMessage = ref('')
const showAddDialog = ref(false)
const ws = WebSocketService
const messagesContainer = ref<HTMLElement | null>(null)
const isAtBottom = ref(true)
const router = useRouter()
const tokenmgr = tokenManager
const friendList = ref<any[]>([])
const groupList = ref<any[]>([])
const allUsersList = ref<any[]>([])
const allGroupsList = ref<any[]>([])

const getChatList = async () => {
    try{
        chatList.value = []
        groupList.value = (await ChatService.getGroupList()).data.groups
        console.warn("groupList", groupList)
        for (const group of groupList.value) {
            chatList.value.push({
                id: group.id,
                name: group.groupname,
                type: 'group',
                lastMessage: group.last_message.message
            })
        }
        friendList.value = (await ChatService.getFriendList()).data.friends
        console.warn("friendList", friendList)
        for (const friend of friendList.value) {
            chatList.value.push({
                id: friend.id,
                name: friend.username,
                type: 'friend',
                lastMessage: friend.last_message.message
            })
        }
        allUsersList.value = (await ChatService.getAllUsers()).data.users
        console.warn("allUsersList", allUsersList)
        allGroupsList.value = (await ChatService.getAllGroups()).data.groups
        console.warn("allGroupsList", allGroupsList)
    }
    catch (error) {
        console.error(error)
    }
}

const selectChat = (chat: ChatItem) => {
    selectedChat.value = chat
    messages.value = []
    
    ws.sendJSON({
        type: 'change_chat',
        friend_id: chat.type === 'friend' ? chat.id : 0,
        group_id: chat.type === 'group' ? chat.id : 0
    })
}

const sendMessage = () => {
    try {
        if (newMessage.value.trim()) {
            const message = {
                type: selectedChat.value?.type === 'friend' ? 'private_message' : 'group_message',
                group_id: selectedChat.value?.type === 'group' ? selectedChat.value.id : 0,
                friend_id: selectedChat.value?.type === 'friend' ? selectedChat.value.id : 0,
                message: newMessage.value
            }
            ws.sendJSON(message)
            messages.value.push({
                content: newMessage.value,
                timestamp: Date.now(),
                sender: 'me'
            })
            scrollToBottom()
            newMessage.value = ''
        }
    }
    catch (error) {
        console.error(error)
        showMessage.error('发送失败，请检查网络连接')
    }
}

const scrollToBottom = (behavior: ScrollBehavior = 'auto') => {
    nextTick(() => {
        if (messagesContainer.value) {
            messagesContainer.value.scrollTo({
                top: messagesContainer.value.scrollHeight,
                behavior: behavior
            })
        }
    })
}

const handleScroll = () => {
    if (!messagesContainer.value) return
    const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
    const threshold = 80
    isAtBottom.value = scrollTop + clientHeight >= scrollHeight - threshold
}

const handleLogout = async () => {
    try {
        await ElMessageBox.confirm(
            '确定要退出登录嘛？', 
            '退出登录', 
            {
                confirmButtonText: '退出',
                cancelButtonText: '取消',
                type: 'warning',
                customClass: 'custom-message-box',
                confirmButtonClass: 'el-button--danger',
                roundButton: true,
            }
        )
        tokenmgr.clearToken()
        router.push('/')        
        showMessage.success('已退出登录')
    } catch (error) {
        showMessage.error('退出登录失败')
    }
}

watch(ws.wsMessage, (message) => {
    if ("type" in message) {
        if (message["type"] === "get_message" && "message" in message && typeof message["message"] === "string") {
            messages.value.push({
                content: message["message"],
                timestamp: Date.now(),
                sender: 'other'
            })
            if(isAtBottom.value) scrollToBottom()
        }
        else if (message.type === "group_messages" && "group_messages" in message && Array.isArray(message["group_messages"])) {
            message["group_messages"].forEach((group_message: JSON) => {
                if ("message" in group_message && typeof group_message["message"] === "string" && "type" in group_message && typeof group_message["type"] === "string") {
                    messages.value.push({
                        content: group_message["message"],
                        timestamp: Date.now(),
                        sender: group_message["type"] === 'received' ? 'other' : 'me'
                    })
                }
            })
            scrollToBottom()
        }
        else if (message.type === "friends_messages" && "friends_messages" in message && Array.isArray(message["friends_messages"])) {
            message["friends_messages"].forEach((friend_message: JSON) => {
                if ("message" in friend_message && typeof friend_message["message"] === "string"
                  && "type" in friend_message && typeof friend_message["type"] === "string"
                  && "created_at" in friend_message && typeof friend_message["created_at"] === "number") {
                    messages.value.push({
                        content: friend_message["message"],
                        timestamp: friend_message["created_at"],
                        sender: friend_message["type"] === 'received' ? 'other' : 'me'
                    })
                }
            })
            scrollToBottom()
        }
    }
    
    
})

const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    })
}

onMounted(() => {
    getChatList()
})
</script>

<script lang="ts">
export default {
    created() {
        if(checkToken() === false) {
            showMessage.error('登录过期，请重新登录')
            this.$router.push('/')
        }
    }
}
</script>
  
<style scoped>
.circle-btn {
    width: 40px;
    height: 40px;
    padding: 0;
    border-radius: 50%;
    background: #07c160;
    border: none !important;
    color: white;
    display: inline-flex;
    justify-content: center;
    align-items: center;
}

.el-icon {
    font-size: 20px;
}

.circle-btn:hover {
    transform: scale(1.1);
}

.chat-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: flex;
    overflow: hidden;
}

.background-image {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url('/bg.jpg') no-repeat center center;
    background-size: cover;
    /* filter: blur(3px); */
    z-index: -1;
}

.main-content {
    display: flex;
    width: 80%;
    height: 80%;
    margin: auto;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(10px);
}

.left-sidebar {
    width: 300px;
    border-right: 1px solid #eee;
    background: rgba(245, 245, 245, 0.8);
    border-radius: 15px 0 0 15px;
}

.header {
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #ddd;
}

.contact-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.contact-list li {
    display: flex;
    align-items: center;
    padding: 15px;
    cursor: pointer;
    transition: background 0.2s;
}

.contact-list li:hover {
    background: rgba(0, 0, 0, 0.05);
}

.contact-list li.active {
    background: rgba(0, 122, 255, 0.1);
}

.avatar {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background: #07c160;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    margin-right: 15px;
}

.right-content {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.chat-area {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.chat-header {
    display: flex;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #eee;
}

.chat-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #07c160;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-right: 15px;
}

.messages-container {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
}

.message-bubble {
    max-width: 70%;
    margin: 10px 0;
    padding: 12px 15px;
    border-radius: 10px;
    position: relative;
}

.message-bubble.sent {
    background: #95ec69;
    margin-left: auto;
}

.message-bubble.received {
    background: white;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.timestamp {
    font-size: 12px;
    color: #666;
    margin-top: 5px;
}

.message-input {
    display: flex;
    padding: 20px;
    border-top: 1px solid #eee;
}

.message-input input {
    flex: 1;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 25px;
    margin-right: 10px;
    outline: none;
}

.message-input button {
    padding: 12px 25px;
    border: none;
    border-radius: 25px;
    background: #07c160;
    color: white;
    cursor: pointer;
}

.empty-chat {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
}

.welcome-text {
    font-size: 24px;
    opacity: 0.5;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

.add-dialog {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 50;
}

.dialog-content {
    background: white;
    padding: 30px;
    border-radius: 10px;
    min-width: 400px;
    overflow: visible;
}

.logout-container {
    position: fixed;
    top: 20px;
    right: 30px;
    z-index: 30;
}

.logout-btn {
    width: 50px;
    height: 50px;
    border: none;
    border-radius: 50%;
    background: linear-gradient(45deg, #ff6b6b, #ff8787);
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.logout-btn:hover {
    transform: translateY(-3px) scale(1.1);
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
}

.icon-signout {
    width: 24px;
    height: 24px;
    background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path d="M832 85H376c-17.7 0-32 14.3-32 32s14.3 32 32 32h456v678H376c-17.7 0-32 14.3-32 32s14.3 32 32 32h456c53 0 96-43 96-96V181c0-53-43-96-96-96zM732.5 507.5L635.4 610c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3l57.1-57.1H192c-17.7 0-32-14.3-32-32s14.3-32 32-32h455.3l-57.1-57.1c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l97.1 97.1c12.5 12.5 12.5 32.8 0 45.3z" fill="white"/></svg>');
    background-size: contain;
}


:deep(.custom-message-box) {
    border-radius: 12px;
    padding: 25px;
    
    .el-message-box__header {
        padding-bottom: 15px;
    }
    
    .el-message-box__content {
        padding: 15px 0;
    }
    
    .el-message-box__btns {
        padding-top: 20px;
    }
}
</style>