<template>
    <div class="handler-wrapper">
        
    </div>
</template>
<script setup lang="ts">
import { useAuthStore } from '@/store/auth';
import { ref } from 'vue';
import { getPanelsByAccesses } from '@/panels';

const currentPage = ref(0)

const authStore = useAuthStore()

const panels = getPanelsByAccesses(authStore.accesses)


</script>
<style scoped>
    
</style>
