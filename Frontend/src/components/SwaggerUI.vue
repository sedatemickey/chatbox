<template>
    <div ref="swaggerContainer"></div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';
import SwaggerUI from 'swagger-ui-dist/swagger-ui-bundle.js';
import 'swagger-ui-dist/swagger-ui.css';

export default defineComponent({
    name: 'SwaggerUI',
    props: {
        specUrl: {
        type: String,
        required: true,
        },  
    },
    setup(props: any) {
        const swaggerContainer = ref<HTMLElement | null>(null);

        onMounted(() => {
            if (swaggerContainer.value) {
                SwaggerUI({
                    url: props.specUrl,
                    domNode: swaggerContainer.value,
                    presets: [
                        SwaggerUI.presets.apis,
                    ],
                });
            }
        });

        return { swaggerContainer };
    },
});
</script>