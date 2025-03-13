<template>
        <div class="markdown-body" v-html="processedContent"></div>
    </template>
    
    <script setup lang="ts">
    import { computed } from 'vue'
    import MarkdownIt from 'markdown-it'
    import hljs from 'highlight.js'
    import dompurify from 'dompurify'
    
    const props = defineProps({
        content: {
            type: String,
            required: true
        }
    })
    
    const md = new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true,
        highlight: (str: string, lang: string) => {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return `<pre class="hljs"><code>${
                        hljs.highlight(str, { language: lang }).value
                    }</code></pre>`
                } catch (__) {}
            }
            return ''
        }
    })
    
    const processedContent = computed(() => {
        const rawHtml = md.render(props.content)
        return dompurify.sanitize(rawHtml)
    })
    </script>
    
    <style>
    @import 'highlight.js/styles/github.css';
    @import 'github-markdown-css/github-markdown.css';
    
    .markdown-body {
        background: transparent !important;
        color: inherit;
        font-size: 15px;
        line-height: 1.6;
    }
    
    .markdown-body pre {
        background-color: rgba(0, 0, 0, 0.05);
        border-radius: 6px;
        padding: 12px;
        overflow-x: auto;
    }
    
    .markdown-body code {
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    }
    
    .markdown-body img {
        max-width: 100%;
        border-radius: 4px;
    }
    
    .markdown-body table {
        border-collapse: collapse;
        margin: 1em 0;
    }
    
    .markdown-body th, 
    .markdown-body td {
        border: 1px solid #dfe2e5;
        padding: 0.6em 1em;
    }
    </style>