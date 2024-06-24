<template>
    <button class="button">
        {{ label }}
    </button>
</template>
<script setup>
import { defineModel } from 'vue';
const label = defineModel('label')
</script>
<script>
export default {
    name: 'purple-button'
}
</script>
<style scoped>
.button {
    height: 54px;
    padding: 10px;
    border-radius: 100px;
    border: none;
    background-color: #993CA6;
    color: #FFFFFF;
    font-family: benzin-regular;
    font-size: 14px;
    font-weight: 400;
}
</style>