<template>
    <transition name="message-fade">
        <div v-if="visible" :class="['message-box', type]">
            <span class="message-icon">
                <component :is="type === 'success' ? SuccessFilled : CircleCloseFilled" style="width: 1em; height: 1em" />
            </span>
            <span class="message-text">{{ message }}</span>
        </div>
    </transition>
</template>
  
<script setup lang="ts">
import { SuccessFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { ref, defineExpose } from 'vue'

type MessageType = 'success' | 'error'

const visible = ref(false)
const message = ref('')
const type = ref<MessageType>('success')

const show = (msg: string, msgType: MessageType = 'success', duration = 3000) => {
    message.value = msg
    type.value = msgType
    visible.value = true
    setTimeout(() => {
        visible.value = false
    }, duration)
}

defineExpose({ show })
</script>
  
<style scoped>
.message-box {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    padding: 12px 24px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    font-size: 14px;
    color: white;
    z-index: 9999;
    transition: all 0.3s ease;
}

.message-box.success {
    background: #67c23a;
    border: 1px solid #85ce61;
}

.message-box.error {
    background: #f56c6c;
    border: 1px solid #f78989;
}

.message-icon {
    margin-right: 12px;
    font-size: 18px;
    display: flex;
    align-items: center;
}

.message-fade-enter-active,
.message-fade-leave-active {
    transition: opacity 0.3s, transform 0.3s;
}

.message-fade-enter-from,
.message-fade-leave-to {
    opacity: 0;
    transform: translate(-50%, -20px);
}
</style>