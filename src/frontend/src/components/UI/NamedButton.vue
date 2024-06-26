<template>
    <div class="button-wrapper" @click="emit('click')">
        <img :class="{active: props.isActive}" :src="props.imgSrc">
        <p :class="{active: props.isActive}">{{ props.label }}</p>
    </div>
</template>
<script setup lang="ts">
const props = defineProps({
    imgSrc: {
        type: String,
        required: true
    },
    label: {
        type: String,
        required: true
    },
    isActive: {
        type: Boolean,
        required: true
    }
})
const emit = defineEmits(['click'])
</script>
<script lang="ts">
export default {
    name: 'named-button'
}
</script>
<style scoped>
.button-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
}
.button-wrapper p {
    font-size: 18px;
    font-family: Stolzl;
    font-weight: 400;
    margin: 0;
    color: #CCCCCC;
}
.button-wrapper .active {
    color: #993CA6;
    filter: none;
}
.button-wrapper img {
    width: 24px;
    height: 24px;
    filter: brightness(1) saturate(100%) invert(77%) sepia(24%) saturate(7%) hue-rotate(59deg) brightness(104%) contrast(89%);
}
</style>