declare module 'swagger-ui-dist/swagger-ui-bundle.js' {
    const SwaggerUI: any
    export default SwaggerUI
}

declare module '@/components/Message.vue' {
    import type { DefineComponent } from 'vue'
    const component: DefineComponent<{}, {}, any>
    export default component
}

declare module '@/views/*' {
    const content: any
    export default content
}

declare module '@/components/FriendGroupModal.vue' {
    const content: any
    export default content
}

declare module 'markdown-it' {
    import MarkdownIt from 'markdown-it/lib'
    export default MarkdownIt
}