<template>
    <div class="friend-group-modal">
        <div class="modal-content">
            <el-icon 
                class="close-btn" 
                @click="$emit('close')"
                :size="24"
                color="#909399"
                style="cursor: pointer"
            >
                <CloseBold />
            </el-icon>
            <el-tabs v-model="activeTab" stretch>
                <el-tab-pane label="好友" name="friends">
                    <div class="tab-content">
                        <div class="add-section">
                            <el-input 
                                v-model="newFriendName" 
                                placeholder="输入好友用户名" 
                                clearable
                                @keyup.enter="handleAddFriend"
                            />
                            <el-button 
                                type="primary" 
                                @click="handleAddFriend"
                                :disabled="!newFriendName"
                            >添加</el-button>
                        </div>

                        <div class="list-section">
                            <h3>我的好友 ({{ friends.length }})</h3>
                            <ul class="user-list">
                                <li v-for="friend in friends" :key="friend.id">
                                    <span>{{ friend.username }}</span>
                                    <el-button 
                                        type="danger" 
                                        size="small"
                                        @click="removeFriend(friend.id)"
                                    >删除</el-button>
                                </li>
                            </ul>
                        </div>

                        <div class="list-section">
                            <h3>所有用户 ({{ allUsers.length }})</h3>
                            <ul class="user-list">
                                <li v-for="user in allUsers" :key="user.id">
                                    <span>{{ user.username }}</span>
                                    <el-button 
                                        type="success" 
                                        size="small"
                                        @click="addExistingFriend(user.id, user.username)"
                                        :disabled="isFriend(user.id)"
                                    >添加</el-button>
                                </li>
                            </ul>
                        </div>
                    </div>
                </el-tab-pane>

                <el-tab-pane label="群组" name="groups">
                    <div class="tab-content">
                        <div class="add-section">
                            <el-input 
                                v-model="newGroupName" 
                                placeholder="输入新群组名称" 
                                clearable
                                @keyup.enter="createGroup"
                            />
                            <el-button 
                                type="primary" 
                                @click="createGroup"
                                :disabled="!newGroupName"
                            >创建群组</el-button>
                        </div>

                        <div class="add-section">
                            <el-input 
                                v-model="newGroupId" 
                                placeholder="输入群组ID" 
                                clearable
                                @keyup.enter="joinGroup"
                            />
                            <el-button 
                                type="success" 
                                @click="joinGroup"
                                :disabled="!newGroupId"
                            >加入群组</el-button>
                        </div>

                        <div class="list-section">
                            <h3>我的群组 ({{ groups.length }})</h3>
                            <ul class="group-list">
                                <li v-for="group in groups" :key="group.id">
                                    <div class="group-info">
                                        <span class="group-name">{{ group.groupname }}</span>
                                        <span class="group-id">ID: {{ group.id }}</span>
                                    </div>
                                    <el-button 
                                        type="danger" 
                                        size="small"
                                        @click="leaveGroup(group.id)"
                                    >退出</el-button>
                                </li>
                            </ul>
                        </div>
                        <div class="list-section">
                            <h3>所有群组 ({{ allGroups.length }})</h3>
                            <ul class="group-list">
                                <li v-for="group in allGroups" :key="group.id">
                                    <span>{{ group.groupname }}</span>
                                    <el-button 
                                        type="success" 
                                        size="small"
                                        @click="joinGroup(group.id)"
                                        :disabled="isinGroup(group.id)"
                                    >加入</el-button>
                                </li>
                            </ul>
                        </div>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script setup>
    const props = defineProps({
        friends: {
            type: Array,
            default: () => []
        },
        allUsers: {
            type: Array,
            default: () => []
        },
        groups: {
            type: Array,
            default: () => []
        },
        allGroups: {
            type: Array,
            default: () => []
        },
        getChatList: {
            type: Function,
            default: () => () => {}
        }
    })
</script>

<script>
import { CloseBold } from '@element-plus/icons-vue'
import userAPI from '@/services/api/user'
import { showMessage } from '@/utils/message'
import ChatService from '@/services/api/chat'
export default {
    components: {
        CloseBold
    },
    data() {
        return {
            activeTab: 'friends',
            newFriendName: '',
            newGroupName: '',
            newGroupId: '',
        }
    },
    methods: {
        async handleAddFriend() {
            if (this.newFriendName) {
                console.error('handleAddFriend')
                bool = await this.addFriend(this.newFriendName)
                if (bool) {
                    this.newFriendName = ''
                }
            }
        },
        async addFriend(username) {
            try {
                const response = await userAPI.addFriend(username)
                showMessage.success('添加好友成功')
                this.getChatList()
                return true
            }
            catch (error) {
                console.log(error)
                showMessage.error('添加好友失败: ' + error.data.detail)
                return false
            }
        },
        async removeFriend(id) {
            try {
                const response = await userAPI.removeFriend(id)
                showMessage.success('移除好友成功')
                this.getChatList()
            }
            catch (error) {
                console.log(error)
                showMessage.error('移除好友失败: ' + error.data.detail)
            }
        },
        addExistingFriend(userId, username) {
            if (!this.isFriend(userId)) {
                this.addFriend(username)
            }
        },
        isFriend(userId) {
            return this.friends.some(f => f.id === userId)
        },
        isinGroup(groupid) {
            return this.groups.some(g => g.id === groupid)
        },
        async createGroup() {
            if (this.newGroupName) {
                try {
                    const response = await userAPI.createGroup(this.newGroupName)
                    showMessage.success('加入群组成功')
                    this.getChatList()
                    this.newGroupName = ''
                    return true
                }
                catch (error) {
                    console.log(error)
                    showMessage.error('加入群组失败: ' + error.data.detail)
                    return false
                }
            }
        },
        async joinGroup(id) {
            if (id) {
                try {
                    const response = await userAPI.joinGroup(id)
                    showMessage.success('加入群组成功')
                    this.getChatList()
                    return true
                }
                catch (error) {
                    console.log(error)
                    showMessage.error('加入群组失败: ' + error.data.detail)
                    return false
                }
            }
        },
        async leaveGroup(id) {
            try {
                const response = await userAPI.removeGroup(id)
                showMessage.success('退出群组成功')
                this.getChatList()
            }
            catch (error) {
                console.log(error)
                showMessage.error('退出群组失败: ' + error.data.detail)
            }
        }
    }
}
</script>

<style scoped>
.friend-group-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    width: 600px;
    max-height: 80vh;
    border-radius: 8px;
    padding: 20px;
    position: relative;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.close-btn {
    position: absolute;
    right: 20px;
    top: 20px;
    z-index: 100;
    transition: color 0.2s;
}

.close-btn:hover {
    color: #606266;
}

.tab-content {
    padding: 10px;
}

.add-section {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.list-section {
    margin: 20px 0;
    border-top: 1px solid #eee;
    padding-top: 15px;
}

h3 {
    color: #666;
    margin-bottom: 10px;
    font-size: 14px;
}

.user-list, .group-list {
    list-style: none;
    padding: 0;
    margin: 0;
    max-height: 300px;
    overflow-y: auto;
}

.user-list li, .group-list li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    margin: 5px 0;
    background: #f8f9fa;
    border-radius: 4px;
    transition: background 0.2s;
}

.user-list li:hover, .group-list li:hover {
    background: #e9ecef;
}

.group-info {
    display: flex;
    flex-direction: column;
}

.group-name {
    font-weight: 500;
    color: #2c3e50;
}

.group-id {
    font-size: 12px;
    color: #666;
}

.el-button {
    transition: all 0.2s;
}
</style>