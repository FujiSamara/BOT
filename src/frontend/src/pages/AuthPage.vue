<template>
    <div class="content">
        <modal-window></modal-window>
    </div>
</template>
<script setup lang="ts">
import ModalWindow from '@/components/ModalWindow.vue'
</script>
<style scoped>
.content {
    background-image: url('img/auth-bg.jpg');
    background-size: cover;
    width: 100%;
    height: 100%;
}
</style>