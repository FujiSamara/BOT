<template>
    <div class="panel-wrapper">
        <img src="/img/logo.svg">
        <div class="menu">
            <div
            class="nav-button"
            v-for="data in props.navigationButtons"
            >
                <named-button
                :img-src="data.imageSrc"
                :label="data.label"
                :is-active="data.isActive"
                :key="data.id"
                @click="$emit('click', data.id)"
                ></named-button>
                <div v-if="data.isActive" class="button-decoration"></div>
            </div>
            
        </div>
        <div class="logout">
            <logout-button
            @click="$emit('logout')"
            ></logout-button>
        </div>
   </div>
</template>
<script setup lang="ts">
import { NavigationButton } from '@/types';

const props = defineProps({
    navigationButtons: {
        type: Array<NavigationButton>,
        required: true
    }
})
const emit = defineEmits(["click", "logout"])
</script>
<style scoped>
.panel-wrapper {
    display: flex;
    flex-direction: column;
    width: 128px;
    gap: 50px;
    padding: 40px 10px 40px 10px;
    align-items: center;
    background-color: #FFFFFF;
    height: fit-content;
}
.panel-wrapper img {
    width: 85px;
}
.menu {
    display: flex;
    flex-direction: column;
    gap: 20px;
    align-items: center;
    width: 100%;
}
.nav-button {
    position: relative;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}
.button-decoration {
    width: 5px;
    position: absolute;
    height: calc(100% + 4px);
    border-radius: 3.5px 0px 0px 3.5px;
    background-color: black;
    right: -10px;
    top: -4px;
    background-color: #993CA6;
}
</style>