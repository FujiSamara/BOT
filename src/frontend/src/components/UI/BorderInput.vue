<template>
    <input :placeholder="placeholder">
</template>
<script setup>
import { defineModel } from 'vue';
const placeholder = defineModel()
</script>
<script>
export default {
    name: 'border-input'
}
</script>
<style scoped>
input {
    border: 1px solid #E8E8E8;
    border-radius: 10px;
    height: 50px;
    padding: 10px 20px 10px 20px;
    -webkit-transition: 0.5s;
    transition: 0.5s;
}

input::placeholder {
    color: #D0D0D0;
    font-weight: 400;
    font-size: 18px;
    font-family: Stolzl;
}

input:focus {
    border-color: #c1c1c1;
    -webkit-transition: 0.5s;
    transition: 0.5s;
    outline: none;
}
</style>