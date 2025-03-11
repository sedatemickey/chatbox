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
